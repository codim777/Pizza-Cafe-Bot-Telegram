from aiogram import Router
from aiogram.types import Message
from aiogram import F
from aiogram.filters import CommandStart, Command
from filters.chat_filters import ChatFilter
from aiogram.types import chat_member_administrator as administr, chat_member_owner as owner
from filters.bad_words import bad_words
from common.routines import remove_punctuation

router=Router()
router.message.filter(ChatFilter(['group','supergroup']))

@router.message(CommandStart())
async def start(message:Message):
    await message.reply('Welcome to Pizza Cafe!')
    
@router.message(Command('admin'))
async def adm(message:Message):
    members=await message.chat.bot.get_chat_administrators(message.chat.id)
    admins=[]
    for member in members:
        if isinstance(member,owner.ChatMemberOwner) or isinstance(member,administr.ChatMemberAdministrator):
        #if member.status=='creator' or member.status=='administrator':
            admins.append(message.from_user.id)
    message.bot.admins=admins
    await message.delete()

@router.message()
async def moder(message:Message):
    if bad_words.intersection(remove_punctuation(message.text.lower()).split(' ')):
        await message.answer(f'{message.from_user.first_name}, mind your speech')
        await message.delete()
        #await message.chat.ban(message.from_user.id)
    
