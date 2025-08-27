from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import StateFilter, or_f
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_category, Post
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Post_category.belong,or_f(F.text.lower()=='food',F.text.lower()=='beverage'))
async def post_category(message:Message,state:FSMContext):
    await state.update_data(belong=message.text.lower())
    await message.answer(f'Set category',reply_markup=template('Back','Cancel',size=(2,)))
    await state.set_state(Post_category.title)
    await message.delete()

@router.message(Post_category.belong, F.text.lower()=='back')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post.option)
    await message.answer('Click an option',reply_markup=template('Category','Item','Cafe','Locale','Cancel',placeholder='Click an option',size=(2,2,1)))
    await message.delete()
    
@router.message(Post_category.belong)
@router.message(Post_category.title, F.text.lower()=='back')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post_category.belong)
    await message.answer(f'Select category family',reply_markup=template('Food','Beverage','Cancel',size=(2,1)))
    await message.delete()

@router.message(Post_category.title, F.text)
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower(),Category.belong==data['belong']))
    await session.close()
    if category is not None:
        await message.answer('Category exists. Set another',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await state.update_data(title=message.text.lower())
    data=await state.get_data()
    await message.answer(f'Set image',reply_markup=template('Back','Cancel',size=(2,)))
    await state.set_state(Post_category.image)
    await message.delete()
    
@router.message(Post_category.title)
async def post_category(message:Message):
    await message.answer('Set category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Post_category.image, F.photo)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Post_category.finish)
    data=await state.get_data()
    await message.answer(f'Post: {data['title']}, {data['belong']}',reply_markup=template('Post','Back','Cancel',size=(2,1)))
    await message.delete()
    
@router.message(Post_category.image, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_category.title)
    await message.answer('Set category',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_category.image)
async def set_image(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()

@router.message(StateFilter(Post_category.finish), F.text.lower()=='post')
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    session.add(Category(title=data['title'],belong=data['belong'],image=data['image']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Post_category.finish),F.text.lower()=='back')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post_category.title)
    await message.answer('Set category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Post_category.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Post: {data['title']}, {data['belong']}',reply_markup=template('Post','Back','Cancel',size=(1,2)))
    await message.delete()