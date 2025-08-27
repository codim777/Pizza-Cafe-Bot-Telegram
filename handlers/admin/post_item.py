from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_item
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Item, Category
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Post_item.category, F.text)
async def post_item(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer('No such category',reply_markup=template('Cancel',size=(1,)))
        return
    await state.update_data(category=message.text.lower())
    await state.set_state(Post_item.name)
    await message.answer('Set item',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.category)
async def post_item(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Post_item.name, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.category)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()

@router.message(Post_item.name, F.text)
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    item=await session.scalar(select(Item).where(Item.category==category.id,Item.name==message.text.lower()))
    await session.close()
    if item is not None:
        await message.answer('Item exists. Set another',reply_markup=template('Back','Cancel',size=(2,)))
        return
    await state.update_data(name=message.text.lower())
    await state.set_state(Post_item.details)
    await message.answer('Set details',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.name)
async def post_item(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.name)
    await message.answer('Set item name',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details, F.text)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(details=message.text.lower())
    await state.set_state(Post_item.image)
    await message.answer('Set image',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details)
async def post_item(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image, F.photo)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Post_item.price)
    await message.answer('Set price',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.details)
    await message.answer('Set details',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image)
async def set_image(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.price, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.image)
    await message.answer('Set image',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(Post_item.price, F.text)
async def set_price(message:Message,state:FSMContext):
    await state.update_data(price=message.text.lower())
    data=await state.get_data()
    await state.set_state(Post_item.finish)
    await message.answer(f'Post: {data['name']} in category {data['category']}, {data['details']}, price: {message.text.lower()}',
        reply_markup=template('Post','Back','Cancel',size=(3,)))
    await message.delete()
    
@router.message(Post_item.price)
async def set_price(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Post_item.finish), F.text.lower()=='post')
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    session.add(Item(name=data['name'],details=data['details'],image=data['image'],price=data['price'],category=category.id))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Post','Update','Delete',size=(3,)))
    await message.delete()
    
@router.message(Post_item.finish, F.text.lower()=='back')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.price)
    await message.answer('Set price',reply_markup=template('Back','Cancel',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Post_item.finish))
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Post: {data['name']} in category {data['category']}, {data['details']}, price: {data['price']}',
        reply_markup=template('Post','Back','Cancel',size=(3,)))
    await message.delete()