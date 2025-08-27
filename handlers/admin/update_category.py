from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Update_category
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select, update

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Update_category.title, F.text)
async def spcify_name(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer('No such category',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(title=message.text.lower())
    await state.set_state(Update_category.prop)
    await message.answer('Specify property',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Update_category.title)
async def name_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel', placeholder='Specify category', size=(1,)))
    await message.delete()
    
@router.message(Update_category.prop, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.title)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_category.prop, F.text)
async def specify_prop(message:Message,state:FSMContext):
    columns=Category.__table__.columns.keys()
    if message.text.lower() not in columns:
        await message.answer('No such property',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await state.update_data(prop=message.text.lower())
    await state.set_state(Update_category.value)
    await message.answer('Set new value',reply_markup=template('Back','Cancel', size=(2,)))
    await message.delete()
    
@router.message(Update_category.prop)
async def prop_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify property', size=(2,)))
    await message.delete()
    
@router.message(Update_category.value, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.prop)
    await message.answer('Specify property',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Update_category.value, F.photo)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']!='image':
        await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
        return
    await state.update_data(value=message.photo[-1].file_id)
    await message.answer(f'Are you sure?',reply_markup=template('Update','Back','Cancel',size=(1,2)))
    await state.set_state(Update_category.finish)
    await message.delete()
    
@router.message(Update_category.value, F.text)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']=='image':
        await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
        return
    await state.update_data(value=message.text.lower())
    await message.answer(f'Update: {data['prop']} = {message.text.lower()}',reply_markup=template('Update','Back','Cancel',size=(1,2)))
    await state.set_state(Update_category.finish)
    await message.delete()
    
@router.message(Update_category.value)
async def value_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_category.finish), F.text.lower()=='update')
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    if data['prop']=='title':
        await session.execute(update(Category).where(Category.title==data['title']).values(title=data['value']))
    elif data['prop']=='image':
        await session.execute(update(Category).where(Category.title==data['title']).values(image=data['value']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Update_category.finish, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.value)
    await message.answer('Set new value',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_category.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Update: {data['prop']} = {data['value']}',reply_markup=template('update','back','cancel', size=(1,2)))
    await message.delete()