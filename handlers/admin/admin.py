from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post,Update,Delete,Post_category,Post_item,Post_cafe,Post_locale,Delete_locale
from fsm.fsm import Update_category,Update_item,Update_cafe,Delete_category,Delete_item,Delete_cafe,Delete_order
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(StateFilter('*'),or_f(Command('admin'),F.text.lower()=='admin',Command('cancel'),F.text.lower()=='cancel'))
async def adm(message:Message,state:FSMContext):
    await message.answer(f'Welcome, <b>{message.from_user.first_name}</b>',reply_markup=template('Post','Update','Delete',size=(3,)))
    status=await state.get_state()
    if status is None:
        return
    await state.clear()
    await message.delete()
    
@router.message(StateFilter(None), or_f(Command('post'), Command('update'), Command('delete')))
@router.message(StateFilter(None), or_f(F.text.lower()=='post', F.text.lower()=='update', F.text.lower()=='delete'))
async def start_posting(message:Message,state:FSMContext):
    text=message.text.lower()
    if text=='post':
        await state.set_state(Post.option)
        await message.answer('Click an option',reply_markup=template('Category','Item','Cafe','Locale','Cancel',
        	placeholder='Click an option',size=(2,2,1)))
    elif text=='update':
        await message.answer('Click an option',reply_markup=template('Category','Item','Cafe','Cancel',placeholder='Click an option',size=(3,1)))
        await state.set_state(Update.option)
    elif text=='delete':
        await state.set_state(Delete.option)
        await message.answer('Click an option',reply_markup=template('Category','Item','Cafe','Locale','Order','Cancel',
        	placeholder='Click an option',size=(2,3,1)))
    await message.delete()

@router.message(Post.option,F.text.lower()=='category')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_category.belong)
    await message.answer('Select category family',reply_markup=template('Food','Beverage','Back','Cancel',size=(2,2)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='item')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_item.category)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='cafe')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_cafe.cafe)
    await message.answer('Set location as follows: <b><i>country, town, street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='locale')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_locale.locale)
    await message.answer('Set locale as follows: <b><i>country, town</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='category')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_category.title)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='item')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_item.category)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='cafe')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.cafe)
    await message.answer('Set location as follows: <b><i>country, town, street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='category')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_category.title)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='item')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_item.category)
    await message.answer('Specify category',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='cafe')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_cafe.cafe)
    await message.answer('Set location as follows: <b><i>country, town, street, house</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='locale')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_locale.locale)
    await message.answer('Specify locale as follows: <b><i>country, town</i></b>',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='order')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_order.id)
    await message.answer('Specify order ID',reply_markup=template('Cancel',size=(1,)))
    await message.delete()
        
@router.message(or_f(StateFilter(Post.option),StateFilter(Update.option),StateFilter(Delete.option)))
async def select_option(message:Message):
    await message.answer('Incorrect input',reply_markup=template('Category','Item','Cafe','Locale','Order','Cancel',size=(3,3)))
    await message.delete()