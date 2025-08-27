from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_order
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Order
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Delete_order.id, F.text)
async def delete_order(message:Message,state:FSMContext):
    session=session_maker()
    order=await session.scalar(select(Order).where(Order.id==message.text.lower()))
    await session.close()
    if order is None:
        await message.answer(f'No such order',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(id=message.text.lower())
    await state.set_state(Delete_order.finish)
    await message.answer(f'Delete order: {message.text.lower()}',reply_markup=template('Delete','Back','Cancel',size=(3,)))
    await message.delete()
        
@router.message(Delete_order.id)
async def delete_order(message:Message,state:FSMContext):
    await message.answer(f'Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
        
@router.message(Delete_order.finish, F.text.lower()=='delete')
async def delete_order(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    await session.execute(delete(Order).where(Order.id==data['id']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Delete_order.finish, F.text.lower()=='back')
async def delete_order(message:Message,state:FSMContext):
    await state.set_state(Delete_order.id)
    await message.answer(f'Specify order ID',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_order.finish))
async def delete_order(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Delete item: {data['id']}',reply_markup=template('Delete','Back','Cancel',size=(1,2)))
    await message.delete()