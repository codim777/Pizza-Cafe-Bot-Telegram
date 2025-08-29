from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from filters.chat_filters import ChatFilter
from keyboard.keyboard import cart_inline, confirm_kb
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import User,Cart,Dest,Cafe,Item, Order, Phone
from sqlalchemy import select, update
from fsm import fsm

router=Router()
router.message.filter(ChatFilter(['private']))

@router.callback_query(StateFilter('*'),F.data.lower()=='cart')
async def make_order(callback:CallbackQuery,state:FSMContext):
    callback.answer('')
    if (await state.get_state()) is not None:
        await state.clear()
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    if user is None:
        session.add(User(tg_id=callback.from_user.id))
        await session.commit()
        user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    if cart is None:
        session.add(Cart(body='',user=user.id))
        await session.commit()
        cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    await session.close()
    if cart.body=='':
        await session.close()
        await state.set_state(fsm.Menu.belong)
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/empty.png'),caption='Cart is empty'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Menu',callback_data='menu')]]))
        return
    await state.set_state(fsm.Order.dest)
    await state.update_data(dest=None)
    await state.set_state(fsm.Order.cafe)
    await state.update_data(cafe=None)
    await state.set_state(fsm.Order.cart)
    content=cart.body.split(', ')
    first=None
    for el in content:
        if el!='':
            first=el
            break
    item=await session.scalar(select(Item).where(Item.name==first.split(' ')[0]))
    await session.close()
    qty=int(first.split(' ')[1])
    price=item.price*qty
    await callback.message.edit_media(InputMediaPhoto(media=item.image,
        caption=f'<b>{item.name.capitalize()}: {qty}, 💰price: {price:.2f}</b>\n{item.details.capitalize()}'),
        reply_markup=cart_inline(content=content,el=first))
		
@router.callback_query(StateFilter(fsm.Order.cart),F.data.lower()=='ok')
async def make_order(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await state.set_state(fsm.Order.delivery)
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=(cart.body).split(', ')
    price=0
    text=''
    for el in content:
        item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
        price=price+item.price*int(el.split(' ')[1])
        text=text+'✅'+el.capitalize()+'\n'
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        caption=f'<b>{text}💰Total price: {price:.2f}</b>'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='By courier',callback_data='courier'),
        InlineKeyboardButton(text='At cafe',callback_data='cafe'),InlineKeyboardButton(text='Menu',callback_data='menu')]]))

@router.callback_query(StateFilter('*'),F.data.startswith('plus_'))
async def make_order(callback:CallbackQuery,state:FSMContext):
    text=callback.data.split('_')[1]
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=cart.body.split(', ')
    body=''
    el=None
    for item in content:
        if text.split(' ')[0]==item.split(' ')[0]:
            qty=int(item.split(' ')[1])
            item=item.split(' ')[0]+' '+str(qty+1)
            el=item
        body=body+item+', '
    body=body[:-2]
    await session.execute(update(Cart).where(Cart.user==user.id).values(body=body))
    await session.commit()
    item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
    await session.close()
    qty=int(el.split(' ')[1])
    price=item.price*qty
    await callback.answer('')
    await callback.message.edit_media(InputMediaPhoto(media=item.image,
        caption=f'<b>{item.name.capitalize()}: {qty}, 💰price: {price:.2f}</b>\n{item.details.capitalize()}'),
        reply_markup=cart_inline(content=body.split(', '),el=el))
    
@router.callback_query(StateFilter('*'),F.data.startswith('minus_'))
async def make_order(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    text=callback.data.split('_')[1]
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=cart.body.split(', ')
    body=''
    el=None
    for item in content:
        if text.lower().split(' ')[0]==item.split(' ')[0]:
            qty=int(item.split(' ')[1])
            if qty>1:
                item=item.split(' ')[0]+' '+str(qty-1)
                el=item
            else:
                continue
        body=body+item+', '
    body=body[:-2]
    await session.execute(update(Cart).where(Cart.user==user.id).values(body=body))
    await session.commit()
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    await callback.answer('')
    content=cart.body.split(', ')
    if len(content)>1 or content[0]!='':
        if el is None:
            for element in content:
                if element!='':
                    el=element
                    break
        item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
        qty=int(el.split(' ')[1])
        price=item.price*qty
        await callback.message.edit_media(InputMediaPhoto(media=item.image,
            caption=f'<b>{item.name.capitalize()}: {qty}, 💰price: {price:.2f}</b>\n{item.details.capitalize()}'),
            reply_markup=cart_inline(content=body.split(', '),el=el))
    else:
        await state.clear()
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/empty.png'),caption='Cart is empty'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Menu',callback_data='menu')]]))
    await session.close()
    
@router.callback_query(StateFilter('*'), F.data.startswith('shift_left_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    text=callback.data.split('_')[2]
    data=await state.get_data()
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    body=cart.body
    content=body.split(', ')
    prev=None
    for el in content:
        if el.split(' ')[0]==text.split(' ')[0]:
            item=await session.scalar(select(Item).where(Item.name==prev.split(' ')[0]))
            await session.close()
            qty=int(prev.split(' ')[1])
            price=item.price*qty
            await callback.message.edit_media(InputMediaPhoto(media=item.image,
            	caption=f'<b>{item.name.capitalize()}: {qty}, 💰price: {price:.2f}</b>\n{item.details.capitalize()}'),
            	reply_markup=cart_inline(content=content,el=prev))
            return
        prev=el

@router.callback_query(StateFilter('*'), F.data.startswith('shift_right_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    text=callback.data.split('_')[2]
    data=await state.get_data()
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    body=cart.body
    content=body.split(', ')
    print(content)
    next=False
    for el in content:
        if next:
            item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
            await session.close()
            qty=int(el.split(' ')[1])
            price=item.price*qty
            await callback.message.edit_media(InputMediaPhoto(media=item.image,
                caption=f'<b>{item.name.capitalize()}: {qty}, 💰price: {price:.2f}</b>\n{item.details.capitalize()}'),
            	reply_markup=cart_inline(content=content,el=el))
            return
        if el.split(' ')[0]==text.split(' ')[0]:
            next=True

@router.callback_query(StateFilter('*'),F.data.startswith('phone_'))
async def make_order(callback:CallbackQuery,state:FSMContext):
    phone=callback.data.lower().split('_')[1]
    await state.set_state(fsm.Order.phone)
    await state.update_data(phone=phone)
    data=await state.get_data()
    await state.set_state(fsm.Order.paid)
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=(cart.body).split(', ')
    price=0
    text=''
    for el in content:
        item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
        price=price+item.price*int(el.split(' ')[1])
        text=text+'✅'+el.capitalize()+'\n'
    if data['delivery']=='by courier':
        if data['dest'] is None:
            if data['room']=='':
                await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {data['country']}, {data['town']}, {data['street']}, {data['house']}\n☎️Contact number: {data['phone']}</b>'), 
                	reply_markup=confirm_kb())
            else:
                await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f},\n\
                🚩Delivery address: {data['country']}, {data['town']}, {data['street']}, {data['house']}, {data['room']}\n\
                ☎️Contact number: {data['phone']}</b>'),reply_markup=confirm_kb())
        else:
            dest=await session.scalar(select(Dest).where(Dest.id==data['dest']))
            if dest.room=='':
                await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {dest.country}, {dest.town}, {dest.street}, {dest.house}\n☎️Contact number: {data['phone']}</b>'),
                	reply_markup=confirm_kb())
            else:
                await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {dest.country}, {dest.town}, {dest.street}, {dest.house}, {dest.room}\n\
                ☎️Contact number: {data['phone']}</b>'),reply_markup=confirm_kb())
        await session.close()
    elif data['delivery']=='at cafe':
        cafe=await session.scalar(select(Cafe).where(Cafe.id==data['cafe']))
        await session.close()
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        🚩Delivery cafe: {cafe.country}, {cafe.town}, {cafe.street}, {cafe.house}\n☎️Contact number: {data['phone']}</b>'),
            reply_markup=confirm_kb())

@router.message(fsm.Order.phone,F.text)
async def make_order(message:Message,state:FSMContext):
    await state.update_data(phone=message.text.lower())
    data=await state.get_data()
    await state.set_state(fsm.Order.paid)
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==message.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=(cart.body).split(', ')
    price=0
    text=''
    for el in content:
        item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
        price=price+item.price*int(el.split(' ')[1])
        text=text+'✅'+el.capitalize()+'\n'
    if data['delivery']=='by courier':
        if data['dest'] is None:
            if data['room']=='':
                await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {data['country']}, {data['town']}, {data['street']}, {data['house']}\n☎️Contact number: {data['phone']}</b>', 
                	reply_markup=confirm_kb())
            else:
                await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f},\n\
                🚩Delivery address: {data['country']}, {data['town']}, {data['street']}, {data['house']}, {data['room']}\n\
                ☎️Contact number: {data['phone']}</b>',reply_markup=confirm_kb())
        else:
            dest=await session.scalar(select(Dest).where(Dest.id==data['dest']))
            if dest.room=='':
                await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {dest.country}, {dest.town}, {dest.street}, {dest.house}\n\
				☎️Contact number: {data['phone']}</b>',reply_markup=confirm_kb())
            else:
                await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
                🚩Delivery address: {dest.country}, {dest.town}, {dest.street}, {dest.house}, {dest.room}\n\
                ☎️Contact number: {data['phone']}</b>',reply_markup=confirm_kb())
        await session.close()
    elif data['delivery']=='at cafe':
        cafe=await session.scalar(select(Cafe).where(Cafe.id==data['cafe']))
        await session.close()
        await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        🚩Delivery cafe: {cafe.country}, {cafe.town}, {cafe.street}, {cafe.house}\n☎️Contact number: {data['phone']}</b>',reply_markup=confirm_kb())
        message.delete()
        
@router.callback_query(StateFilter(fsm.Order.paid),F.data.lower()=='pay')
async def make_order(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    data=await state.get_data()
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    id=0
    if data['delivery']=='by courier':
        if data['dest']==None:
            await session.commit()
            if data['room']=='':
                order=Order(cart=f'{cart.body}',dest=f'{data['country']},{data['town']},{data['street']},{data['house']}',
                    cafe='',delivery='by courier',phone=f'{data['phone']}',user=user.id)
                session.add(order)
                await session.flush()
                id=order.id
                await session.commit()
            else:
                order=Order(cart=f'{cart.body}',dest=f'{data['country']},{data['town']},{data['street']},{data['house']},{data['room']}',
                    cafe='',delivery='by courier',phone=f'{data['phone']}',user=user.id)
                session.add(order)
                await session.flush()
                id=order.id
                await session.commit()
            dest=await session.scalar(select(Dest).where(Dest.country==data['country'],Dest.town==data['town'],Dest.street==data['street'],
                    Dest.house==data['house'],Dest.room==data['room'],Dest.user==user.id))
            if dest is None:
                session.add(Dest(country=data['country'],town=data['town'],street=data['street'],house=data['house'],room=data['room'],user=user.id))
                await session.commit()
        else:
            dest=await session.scalar(select(Dest).where(Dest.id==data['dest']))
            if dest.room=='':
                order=Order(cart=f'{cart.body}',dest=f'{dest.country},{dest.town},{dest.street},{dest.house}',
                	cafe='',delivery='by courier',phone=f'{data['phone']}',user=user.id)
                session.add(order)
                await session.flush()
                id=order.id
                await session.commit()
            else:
                order=Order(cart=f'{cart.body}',dest=f'{dest.country},{dest.town},{dest.street},{dest.house},{dest.room}',
                	cafe='',delivery='by courier',phone=f'{data['phone']}',user=user.id)
                session.add(order)
                await session.flush()
                id=order.id
                await session.commit()
    elif data['delivery']=='at cafe':
        cafe=await session.scalar(select(Cafe).where(Cafe.id==data['cafe']))
        order=Order(cart=f'{cart.body}',cafe=f'{cafe.country},{cafe.town},{cafe.street},{cafe.house}',
            dest='',delivery='at cafe',phone=f'{data['phone']}',user=user.id)
        session.add(order)
        await session.flush()
        id=order.id
        await session.commit()
    phone=await session.scalar(select(Phone).where(Phone.number==data['phone'],Phone.user==user.id))
    if phone is None:
        session.add(Phone(number=data['phone'], user=user.id))
        await session.commit()
    await session.close()
    await state.clear()
    await state.set_state(fsm.Menu.belong)
    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile('common/accept.png'),
        caption=f'Thank you. You order is accepted with ID=<b>{id}</b>'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Menu',callback_data='menu')]]))