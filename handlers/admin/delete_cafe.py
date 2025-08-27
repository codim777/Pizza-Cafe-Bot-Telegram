from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_cafe
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Delete_cafe.cafe, F.text)
async def delete_cafe(message:Message,state:FSMContext):
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
    await state.set_state(Delete_cafe.finish)
    await message.answer(f'Delete cafe: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Delete','Back','Cancel',size=(3,)))
    await message.delete()
    
@router.message(Delete_cafe.cafe)
async def delete_cafe(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_cafe.finish),F.text.lower()=='delete')
async def delete_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    await session.execute(delete(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Delete_cafe.finish),F.text.lower()=='back')
async def delete_cafe(message:Message,state:FSMContext):
    await state.set_state(Delete_cafe.cafe)
    await message.answer('Specify locale as follows: <b><i>country, town, street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()

@router.message(StateFilter(Delete_cafe.finish))
async def delete_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    text=(data['cafe']).split(', ')
    await message.answer(f'Delete cafe: {text[0]}, {text[1], text[2], text[3]}',reply_markup=template('Delete','Back','Cancel',size=(3,)))
    await message.delete()