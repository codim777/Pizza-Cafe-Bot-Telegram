from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_item
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Item,Category
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Delete_item.category, F.text)
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
    await state.set_state(Delete_item.name)
    await message.delete()
    
@router.message(Delete_item.category)
async def name_check(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete_item.name, F.text)
async def delete_item(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    item=await session.scalar(select(Item).where(Item.category==category.id, Item.name==message.text.lower()))
    await session.close()
    if item is None:
        await message.answer(f'No such item',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(name=message.text.lower())
    await state.set_state(Delete_item.finish)
    await message.answer(f'Delete item: {message.text.lower()}',reply_markup=template('Delete','Back','Cancel',size=(3,)))
    await message.delete()
        
@router.message(Delete_item.name)
async def delete_item(message:Message,state:FSMContext):
    await message.answer(f'Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
        
@router.message(Delete_item.finish, F.text.lower()=='delete')
async def delete_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    await session.execute(delete(Item).where(Item.name==data['name']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Delete_item.finish, F.text.lower()=='back')
async def delete_item(message:Message,state:FSMContext):
    await state.set_state(Delete_item.name)
    await message.answer(f'Specify item',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_item.finish))
async def delete_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Delete item: {data['name']}',reply_markup=template('Delete','Back','Cancel',size=(1,2)))
    await message.delete()