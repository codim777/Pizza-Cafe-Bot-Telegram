from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from filters.chat_filters import ChatFilter
from fsm import fsm
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Dest, Locale, Cafe, Cart, Item, User, Phone
from sqlalchemy import select
from keyboard.keyboard import dest_countries_kb, cafe_countries_kb, dest_towns_kb, cafe_towns_kb, dest_kb, cafe_kb, phone_kb, phones_kb

router=Router()
router.message.filter(ChatFilter(['private']))

@router.callback_query(fsm.Order.delivery,F.data.lower()=="courier")
async def delivery(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await state.update_data(delivery='by courier')
    await state.set_state(fsm.Order.dest)
    session=session_maker()
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    dest=await session.scalar(select(Dest).where(Dest.user==user.id))
    if dest is None:
        await state.set_state(fsm.Order.country)
        countries=await session.scalars(select(Locale))
        await session.close()
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),caption='Select country'),
            	reply_markup=dest_countries_kb(countries.all()))
        return
    dests=await session.scalars(select(Dest).where(Dest.user==user.id))
    await session.close()
    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile('common/location.png'),
            caption='Select or set address'),reply_markup=dest_kb(dests.all()))
    
@router.callback_query(fsm.Order.delivery,F.data.lower()=="cafe")
async def delivery(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await state.update_data(delivery='at cafe')
    await state.set_state(fsm.Order.country)
    session=session_maker()
    cafes=await session.scalars(select(Cafe))
    await session.close()
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
    		caption=f'Select country'),reply_markup=cafe_countries_kb(cafes.all()))

@router.callback_query(StateFilter('*'),F.data.lower()=="address")
async def delivery(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await state.set_state(fsm.Order.country)
    session=session_maker()
    locales=await session.scalars(select(Locale))
    await session.close()
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
            caption=f'Select country'),reply_markup=dest_countries_kb(locales.all()))
    
@router.callback_query(fsm.Order.dest,F.data.startswith('dest__'))
async def delivery(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    addr=callback.data.lower().split('__')[1].split('_')
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
    dest=None
    phone=await session.scalar(select(Phone).where(Phone.user==user.id))
    if len(addr)==4:
        dest=await session.scalar(select(Dest).where(Dest.country==addr[0],Dest.town==addr[1],Dest.street==addr[2],Dest.house==addr[3],Dest.room==''))
        if phone is None:
            await state.set_state(fsm.Order.phone)
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        		🚩Address: {addr[0].capitalize()}, {addr[0].capitalize()}, {addr[2].capitalize()}, {addr[3]}</b>\nSet phone number'),
        		reply_markup=phone_kb())
        else:
            phones=await session.scalars(select(Phone).where(Phone.user==user.id))
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        		🚩Address: {addr[0].capitalize()}, {addr[0].capitalize()}, {addr[2].capitalize()}, {addr[3]}</b>\nSelect or set phone number'),
        		reply_markup=phones_kb(phones.all()))
    else:
        dest=await session.scalar(select(Dest).where(Dest.country==addr[0],Dest.town==addr[1],Dest.street==addr[2],Dest.house==addr[3],Dest.room==addr[4]))
        if phone is None:
            await state.set_state(fsm.Order.phone)
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
            	🚩Address: {addr[0].capitalize()}, {addr[1].capitalize()}, {addr[2].capitalize()}, {addr[3]}, {addr[4]}</b>\nSet phone number'),
            	reply_markup=phone_kb())
        else:
            phones=await session.scalars(select(Phone).where(Phone.user==user.id))
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
            	🚩Address: {addr[0].capitalize()}, {addr[1].capitalize()}, {addr[2].capitalize()}, {addr[3]}, {addr[4]}</b>\n\
                Select or set phone number'),reply_markup=phones_kb(phones.all()))
    await session.close()
    await state.update_data(dest=dest.id)
    
@router.callback_query(fsm.Order.country, F.data.startswith('dest_country_'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    country=callback.data.split('_')[2]
    await state.update_data(country=country.lower())
    await state.set_state(fsm.Order.town)
    session=session_maker()
    towns=await session.scalars(select(Locale).where(Locale.country==country.lower()))
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
    		caption=f'<b>{country.lower().capitalize()}</b>\nSelect town'),reply_markup=dest_towns_kb(towns.all()))
    await session.close()
    
@router.callback_query(fsm.Order.country, F.data.startswith('cafe_country_'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    data=await state.get_data()
    country=callback.data.split('_')[2]
    await state.update_data(country=country.lower())
    await state.set_state(fsm.Order.town)
    session=session_maker()
    cafes=await session.scalars(select(Cafe).where(Cafe.country==country.lower()))
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
        caption=f'<b>{country.lower().capitalize()}</b>\nSelect town'),reply_markup=cafe_towns_kb(cafes.all()))
    await session.close()
    
@router.callback_query(fsm.Order.town, F.data.startswith('dest_town_'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    town=callback.data.split('_')[2]
    data=await state.get_data()
    await state.update_data(town=town.lower())
    await state.set_state(fsm.Order.street)
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
        caption=f'<b>{data['country'].capitalize()}, {town.capitalize()}</b>\nSet address as follows: \
        <b>street, house, room</b> if there is room number, otherwise: <b>street, house</b>'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Cancel',callback_data='cancel')]]))

@router.callback_query(fsm.Order.town, F.data.startswith('cafe_town_'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    town=callback.data.split('_')[2]
    data=await state.get_data()
    await state.update_data(town=town.lower())
    await state.set_state(fsm.Order.cafe)
    session=session_maker()
    cafes=await session.scalars(select(Cafe).where(Cafe.country==data['country'], Cafe.town==town.lower()))
    await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/location.png'),
    		caption=f'<b>{data['country'].capitalize()}, {town.capitalize()}</b>\nSelect cafe'),reply_markup=cafe_kb(cafes.all()))
    await session.close()
    
@router.callback_query(fsm.Order.cafe, F.data.startswith('cafe__'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    addr=callback.data.lower().split('__')[1].split('_')
    session=session_maker()        
    cafe=await session.scalar(select(Cafe).where(Cafe.country==addr[0],Cafe.town==addr[1],Cafe.street==addr[2],Cafe.house==addr[3]))
    await state.update_data(cafe=cafe.id)
    user=await session.scalar(select(User).where(User.tg_id==callback.from_user.id))
    cart=await session.scalar(select(Cart).where(Cart.user==user.id))
    content=(cart.body).split(', ')
    price=0
    text=''
    for el in content:
        item=await session.scalar(select(Item).where(Item.name==el.split(' ')[0]))
        price=price+item.price*int(el.split(' ')[1])
        text=text+'✅'+el.capitalize()+'\n'
    phone=await session.scalar(select(Phone).where(Phone.user==user.id))
    if phone is None:
        await state.set_state(fsm.Order.phone)
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'{text}💰Total price: {price:.2f}\n\
        	🚩Address: {addr[0].capitalize()}, {addr[1].capitalize()}, {addr[2].capitalize()}, {addr[3]}\nSet phone number'),
        	reply_markup=phone_kb())
    else:
        phones=await session.scalars(select(Phone).where(Phone.user==user.id))
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),caption=f'{text}💰Total price: {price:.2f}\n\
        	🚩Address: {addr[0].capitalize()}, {addr[1].capitalize()}, {addr[2].capitalize()}, {addr[3]}\nSelect or set phone number'),
        	reply_markup=phones_kb(phones.all()))
    await session.close()
    
@router.callback_query(StateFilter('*'),F.data.contains('another_phone'))
async def set_name(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await state.set_state(fsm.Order.phone)
    data=await state.get_data()
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
    if data['delivery']=='by courier' and data['dest'] is None:
        if data['room']=='':
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        		caption=f'{text}💰Total price: {price:.2f}\n🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, \
            	{data['street'].capitalize()}, {data['house']}\nSet phone number'),reply_markup=phone_kb())
        else:
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        		caption=f'{text}💰Total price: {price:.2f}\n🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, \
            	{data['street'].capitalize()}, {data['house']}, {data['room']}\nSet phone number'),reply_markup=phone_kb())
    elif data['delivery']=='by courier' and data['dest'] is not None:
        dest=await session.scalar(select(Dest).where(Dest.id==data['dest']))
        if dest.room=='':
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        		caption=f'{text}💰Total price: {price:.2f}\n🚩Address: {dest.country.capitalize()}, {dest.town.capitalize()}, \
            	{dest.street.capitalize()}, {dest.house}\nSet phone number'),reply_markup=phone_kb())
        else:
            await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        		caption=f'{text}💰Total price: {price:.2f}\n🚩Address: {dest.country.capitalize()}, {dest.town.capitalize()}, \
            	{dest.street.capitalize()}, {dest.house}, {dest.room}\nSet phone number'),reply_markup=phone_kb())
    else:
        cafe=await session.scalar(select(Cafe).where(Cafe.id==data['cafe']))
        await callback.message.edit_media(InputMediaPhoto(media=FSInputFile('common/order.png'),
        	caption=f'{text}💰Total price: {price:.2f}\n🚩Address: {cafe.country.capitalize()}, {cafe.town.capitalize()}, \
            {cafe.street.capitalize()}, {cafe.house}\nSet phone number'),reply_markup=phone_kb())
    await session.close()    
    
@router.message(fsm.Order.street, F.text)
async def set_image(message:Message,state:FSMContext):
    addr=message.text.lower().split(', ')
    data=await state.get_data()
    if len(addr)<2 or len(addr)>3:
        await message.answer(f'<b>{data['country'].capitalize()}, {data['town'].capitalize()}</b>\nSet address as follows: \
        <b>street, house, room</b> if there is room number, otherwise: <b>street, house</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Cancel',callback_data='cancel')]]))
        await message.delete()
        return
    await state.update_data(street=addr[0])
    await state.set_state(fsm.Order.house)
    await state.update_data(house=addr[1])
    await state.set_state(fsm.Order.room)
    if len(addr)==2:
        await state.update_data(room='')
    else:
        await state.update_data(room=addr[2])
    await state.set_state(fsm.Order.phone)
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
    phone=await session.scalar(select(Phone).where(Phone.user==user.id))
    if len(addr)==2:
        if phone is None:
            await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        	🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, {addr[0].capitalize()}, {addr[1]}</b>\nSet phone number',
        		reply_markup=phone_kb())
        else:
            phones=await session.scalars(select(Phone).where(Phone.user==user.id))
            await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        	🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, {addr[0].capitalize()}, {addr[1]}</b>\n\
            Select or set phone number',reply_markup=phones_kb(phones.all()))
    else:
        if phone is None:
            await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        	🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, {addr[0].capitalize()}, {addr[1]}, {addr[2]}</b>\n\
            Set phone number',reply_markup=phone_kb())
        else:
            phones=await session.scalars(select(Phone).where(Phone.user==user.id))
            await message.answer_photo(FSInputFile('common/order.png'),caption=f'<b>{text}💰Total price: {price:.2f}\n\
        	🚩Address: {data['country'].capitalize()}, {data['town'].capitalize()}, {addr[0].capitalize()}, {addr[1]}, {addr[2]}</b>\n\
            Select or set phone number',reply_markup=phones_kb(phones.all()))
    await session.close()
    await message.delete()
    
@router.message(fsm.Order.street)
async def set_name(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'<b>{data['country'].capitalize()}, {data['town'].capitalize()}</b>\nSet address as follows: \
        <b>street, house, room</b> if there is room number, otherwise: <b>street, house</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Cancel',callback_data='cancel')]]))
    await message.delete()