from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Update_item
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Item, Category
from sqlalchemy import select,update

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Update_item.category, F.text)
async def specify_name(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    if category is None:
        await message.answer('No such category',reply_markup=template('Cancel',size=(1,)))
        await session.close()
        return
    item=await session.scalar(select(Item).where(Item.category==category.id))
    await session.close()
    if item is None:
        await message.answer('No item of such category',reply_markup=template('Cancel',size=(1,)))
        return
    await message.answer('Specify name',reply_markup=template('Back','Cancel',size=(2,)))
    await state.update_data(category=message.text.lower())
    await state.set_state(Update_item.name)
    await message.delete()
    
@router.message(Update_item.category)
async def name_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_item.name, F.text)
async def specify_name(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    item=await session.scalar(select(Item).where(Item.category==category.id, Item.name==message.text.lower()))
    await session.close()
    if item is None:
        await message.answer('No such item',reply_markup=template('Cancel',size=(1,)))
        return
    await message.answer('Specify property',reply_markup=template('Back','Cancel',size=(2,)))
    await state.update_data(name=message.text.lower())
    await state.set_state(Update_item.prop)
    await message.delete()
    
@router.message(Update_item.name)
async def name_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_item.prop, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_item.name)
    await message.answer('Specify item',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update_item.prop, F.text)
async def specify_prop(message:Message,state:FSMContext):
    columns=Item.__table__.columns.keys()
    if message.text.lower() not in columns:
        await message.answer('No such property',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await state.update_data(prop=message.text.lower())
    await state.set_state(Update_item.value)
    await message.answer('Set new value',reply_markup=template('Back','Cancel', size=(2,)))
    await message.delete()
    
@router.message(Update_item.prop)
async def prop_check(message:Message):
    await message.answer('Incorrect input. Try again',reply_markup=template('Back','Cancel',placeholder='Specify property', size=(2,)))
    await message.delete()
    
@router.message(Update_item.value, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_item.prop)
    await message.answer('Specify property',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()

@router.message(Update_item.value, F.photo)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']!='image':
        await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
        return
    await state.update_data(value=message.photo[-1].file_id)
    await message.answer(f'Are you sure?',reply_markup=template('Update','Back','Cancel',size=(1,2)))
    await state.set_state(Update_item.finish)
    await message.delete()
    
@router.message(Update_item.value, F.text)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']=='image':
        await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
        return
    await state.update_data(value=message.text.lower())
    await message.answer(f'Update: {data['prop']} = {message.text.lower()}',reply_markup=template('Update','Back','Cancel',size=(1,2)))
    await state.set_state(Update_item.finish)
    await message.delete()
    
@router.message(Update_item.value)
async def value_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel', placeholder='Specify new value', size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_item.finish), F.text.lower()=='update')
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    if data['prop']=='name':
        await session.execute(update(Item).where(Item.name==data['name']).values(name=data['value']))
    elif data['prop']=='details':
        await session.execute(update(Item).where(Item.name==data['name']).values(details=data['value']))
    if data['prop']=='image':
        await session.execute(update(Item).where(Item.name==data['name']).values(image=data['value']))
    if data['prop']=='price':
        await session.execute(update(Item).where(Item.name==data['name']).values(price=data['value']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Update_item.finish, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_item.value)
    await message.answer('Set new value',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_item.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'nUpdate: {data['prop']} = {data['value']}',reply_markup=template('Update','Back','Cancel', size=(3,)))
    await message.delete()