from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Update_cafe
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select, update

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Update_cafe.cafe, F.text)
async def update_cafe(message:Message,state:FSMContext):
    text=message.text.lower().split(', ')
    if len(text)!=4:
        await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
        return
    session=session_maker()
    cafe=await session.scalar(select(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.close()
    if cafe is None:
        await message.answer('No such cafe',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(cafe=message.text.lower())
    await state.set_state(Update_cafe.prop)
    await message.answer('Specify property to update',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.cafe)
async def update_cafe(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_cafe.prop, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.cafe)
    await message.answer('Specify locale as follows: <b><i>country, town, street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_cafe.prop, F.text)
async def update_cafe(message:Message,state:FSMContext):
    columns=Cafe.__table__.columns.keys()
    if message.text.lower() not in columns:
        await message.answer('No such property',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await message.answer('Set new value',reply_markup=template('Back','Cancel', size=(2,)))
    await state.update_data(prop=message.text.lower())
    await state.set_state(Update_cafe.value)
    await message.delete()
    
@router.message(Update_cafe.prop)
async def update_cafe(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify property to update', size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.value, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.prop)
    await message.answer('Specify property to update',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.value, F.text)
async def update_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.update_data(value=message.text.lower())
    await message.answer(f'Update: {data['prop']} = {message.text.lower()}',reply_markup=template('Update','Back','Cancel', size=(3,)))
    await state.set_state(Update_cafe.finish)
    await message.delete()
    
@router.message(Update_cafe.value)
async def update_cafe(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Set new value', size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_cafe.finish), F.text.lower()=='update')
async def update_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    if data['prop']=='country':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(country=data['value']))
    elif data['prop']=='town':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(town=data['value']))
    elif data['prop']=='street':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(street=data['value']))
    elif data['prop']=='house':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(house=data['value']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Update_cafe.finish, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.value)
    await message.answer('Set new value',reply_markup=template('Back','Cancel', size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_cafe.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Update: {data['prop']} = {data['value']}',reply_markup=template('Update','Back','Cancel', size=(3,)))
    await message.delete()