from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_cafe
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Post_cafe.cafe, F.text)
async def post_cafe(message:Message,state:FSMContext):
    text=message.text.lower().split(', ')
    if len(text)!=4:
        await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
        return
    session=session_maker()
    cafe=await session.scalar(select(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.close()
    if cafe is not None:
        await message.answer('Cafe exists. Set another',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await state.update_data(cafe=message.text.lower())
    await state.set_state(Post_cafe.finish)
    await message.answer(f'Post: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Post','Back','Cancel',size=(3,)))
    await message.delete()
    
@router.message(Post_cafe.cafe)
async def post_cafe(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Post_cafe.finish),F.text.lower()=='post')
async def post_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    session.add(Cafe(country=text[0],town=text[1],street=text[2],house=text[3]))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Post_cafe.finish),F.text.lower()=='back')
async def post_cafe(message:Message,state:FSMContext):
    await state.set_state(Post_cafe.cafe)
    await message.answer('Set location as follows: <b><i>Country, Town, Street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()

@router.message(StateFilter(Post_cafe.finish))
async def post_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    text=(data['cafe']).split(', ')
    await message.answer(f'Post: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Post','Back','Cancel',size=(3,)))
    await message.delete()
