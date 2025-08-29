from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_category
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Delete_category.title, F.text)
async def delete_category(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer(f'No such category',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(title=message.text.lower())
    await state.set_state(Delete_category.finish)
    await message.answer(f'Delete category: {message.text.lower()}',reply_markup=template('Delete','Back','Cancel',size=(3,)))
    await message.delete()
        
@router.message(Delete_category.title)
async def delete_category(message:Message,state:FSMContext):
    await message.answer(f'Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
        
@router.message(Delete_category.finish, F.text.lower()=='delete')
async def delete_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    await session.execute(delete(Category).where(Category.title==data['title']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Delete_category.finish, F.text.lower()=='back')
async def delete_category(message:Message,state:FSMContext):
    await state.set_state(Delete_category.title)
    await message.answer(f'Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_category.finish))
async def delete_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Delete category: {data['title']}',reply_markup=template('Delete','Back','Cancel',size=(1,2)))
    await message.delete()