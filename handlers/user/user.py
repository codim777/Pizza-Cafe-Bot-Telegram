from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.filters import StateFilter, CommandStart, or_f
from filters.chat_filters import ChatFilter
from keyboard.keyboard import families_kb, categories_kb, template_inline
from fsm.fsm import Menu
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_marked_section, Bold
from database.engine import session_maker
from database.models import Category, Item, Cart, User
from sqlalchemy import select, update

router=Router()
router.message.filter(ChatFilter(['private']))

@router.message(StateFilter('*'),CommandStart())
async def menu(message:Message,state:FSMContext):
    status=await state.get_state()
    if status is not None:
        await state.clear()
    await state.set_state(Menu.belong)
    await message.answer_photo(photo=FSInputFile('common/welcome.png'),reply_markup=families_kb())

@router.callback_query(StateFilter('*'), or_f(F.data.lower()=='cancel',F.data.lower()=='menu'))
async def menu(callback:CallbackQuery,state:FSMContext):
    status=await state.get_state()
    if status is not None:
        await state.clear()
    await state.set_state(Menu.belong)
    await callback.answer('')
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/welcome.png')),reply_markup=families_kb())
    
@router.callback_query(StateFilter('*'),or_f(F.data.lower()=='food',F.data.lower()=='beverage'))
async def menu(callback:CallbackQuery,state:FSMContext):
    session=session_maker()
    categories=(await session.scalars(select(Category).where(Category.belong==callback.data.lower()))).all()
    print(categories)
    await session.close()
    await state.update_data(belong=callback.data.lower())
    await state.set_state(Menu.category)
    await callback.answer('')
    for category in categories:
        await callback.message.edit_media(InputMediaPhoto(media=category.image,caption=f'<b>{category.title.capitalize()}</b>'),
            reply_markup=categories_kb(categories,category.id))
        break
    
@router.callback_query(Menu.category, F.data.startswith('category_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    #await state.set_state(Menu.finish)
    category_id=int(callback.data.split('_')[1])
    session=session_maker()
    items=(await session.scalars(select(Item).where(Item.category==category_id))).all()
    print(items)
    await session.close()
    await state.update_data(category=category_id)
    for item in items:
        await callback.message.edit_media(InputMediaPhoto(media=item.image,
            caption=f'<b>{item.name.capitalize()}, 💰price: {item.price:.2f}</b>\n{item.details.capitalize()}'),
            reply_markup=template_inline(items,item.id))
        break
    
@router.callback_query(StateFilter('*'),F.data.contains('to_family_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    category_id=int(callback.data.split('_')[2])
    session=session_maker()
    #category=await session.scalar(select(Category).where(Category.id==category_id))
    categories=(await session.scalars(select(Category).where(Category.belong==category.belong))).all()
    await session.close()
    await state.set_state(Menu.category)
    await callback.answer('')
    for category in categories:
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/welcome.png'),caption=f'<b>{category.title.capitalize()}</b>'),
        	reply_markup=categories_kb(categories,category_id))
        break
    
@router.callback_query(StateFilter('*'), F.data.startswith('add_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    data=await state.get_data()
    id=int(callback.data.split('_')[1])
    session=session_maker()
    item_info=await session.scalar(select(Item).where(Item.id==id))
    items=await session.scalars(select(Item).where(Item.category==data['category']))
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
    content=cart.body.split(', ')
    body=''
    exist=False
    length=len(content)
    count=1
    for item in content:
        if item_info.name==item.split(' ')[0]:
            exist=True
            qty=int(item.split(' ')[1])
            item=item.split(' ')[0]+' '+str(qty+1)
        body+=item
        if count<length:
            body+=', '
        count+=1
    if exist==False:
        if cart.body=='':
            await session.execute(update(Cart).where(Cart.user==user.id).values(body=(item_info.name+' 1')))
        else:
            await session.execute(update(Cart).where(Cart.user==user.id).values(body=(cart.body+', '+item_info.name+' 1')))
    else:
        await session.execute(update(Cart).where(Cart.user==user.id).values(body=body))
    await session.commit()
    await session.close()
    await callback.answer('')
    await callback.message.edit_media(InputMediaPhoto(media=item_info.image,
            caption=f'<b>{item_info.name.capitalize()}, 💰price: {item_info.price:.2f}</b>\n{item_info.details.capitalize()}'),
            reply_markup=template_inline(items.all(),item_info.id))
    
@router.callback_query(StateFilter('*'), F.data.startswith('left_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    id=int(callback.data.split('_')[1])
    data=await state.get_data()
    session=session_maker()
    items=(await session.scalars(select(Item).where(Item.category==data['category']))).all()
    await session.close()
    prev=None
    for item in items:
        if item.id==id:
            await callback.message.edit_media(InputMediaPhoto(media=prev.image,
                caption=f'<b>{prev.name.capitalize()}, 💰price: {prev.price:.2f}</b>\n{prev.details.capitalize()}'),
                reply_markup=template_inline(items,prev.id))
            return
        prev=item
        
@router.callback_query(StateFilter('*'), F.data.startswith('offset_left_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    id=int(callback.data.split('_')[2])
    data=await state.get_data()
    session=session_maker()
    categories=(await session.scalars(select(Category).where(Category.belong==data['belong']))).all()
    await session.close()
    prev=None
    for category in categories:
        if category.id==id:
            await callback.message.edit_media(InputMediaPhoto(media=prev.image,caption=f'<b>{prev.title.capitalize()}</b>'),
                reply_markup=categories_kb(categories,prev.id))
            return
        prev=category

@router.callback_query(StateFilter('*'), F.data.startswith('right_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    id=int(callback.data.split('_')[1])
    data=await state.get_data()
    session=session_maker()
    items=(await session.scalars(select(Item).where(Item.category==data['category']))).all()
    await session.close()
    next=False
    for item in items:
        if next:
            await callback.message.edit_media(InputMediaPhoto(media=item.image,
                caption=f'<b>{item.name.capitalize()}, 💰price: {item.price:.2f}</b>\n{item.details.capitalize()}'),
                reply_markup=template_inline(items,item.id))
            return
        if item.id==id:
            next=True
            
@router.callback_query(StateFilter('*'), F.data.startswith('offset_right_'))
async def menu(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    id=int(callback.data.split('_')[2])
    data=await state.get_data()
    session=session_maker()
    categories=(await session.scalars(select(Category).where(Category.belong==data['belong']))).all()
    print(categories)
    await session.close()
    next=False
    for category in categories:
        if next:
            await callback.message.edit_media(InputMediaPhoto(media=category.image,
                caption=f'<b>{category.title.capitalize()}</b>'),reply_markup=categories_kb(categories,category.id))
            return
        if category.id==id:
            next=True
 
@router.callback_query(StateFilter('*'),F.data.lower()=='feedback')
async def start(callback:CallbackQuery,state:FSMContext):
    await state.set_state(Menu.feedback)
    await callback.answer('')
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/welcome.png'),caption='Leave your feedback below'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=([[InlineKeyboardButton(text='Send',callback_data='send'),
                InlineKeyboardButton(text='Menu',callback_data='menu')]])))
    
@router.callback_query(StateFilter('*'),F.data.lower()=='about')
async def start(callback:CallbackQuery):
    await callback.answer('')
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/welcome.png'),caption=f'Our head office is located in Kazan.\n\n\
        {as_marked_section(
        	Bold('How to pay:'),
            'By card online',
            'By cash at cafe',
            'By card at cafe' ).as_html()},\n\n\
        {as_marked_section(
            Bold('Delivery:'),
            'At cafe',
            'By courier').as_html()}'),reply_markup=InlineKeyboardMarkup(inline_keyboard=([[InlineKeyboardButton(text='Menu',callback_data='menu')]])))
    
