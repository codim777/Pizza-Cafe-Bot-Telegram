from aiogram.filters import Filter
from aiogram.types import Message

class ChatFilter(Filter):
    def __init__(self,chat_types:list[str]):
        self.chat_types=chat_types 
    async def __call__(self,message:Message):
        return message.chat.type in self.chat_types
    
class AdminFilter(Filter):
    def __init__(self):
        pass
    async def __call__(self,message:Message):
        return len(message.bot.admins)>0 and message.from_user.id in message.bot.admins