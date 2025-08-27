from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from os import getenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers.admin.admin import router as admin_router
from handlers.admin.post_item import router as post_item_router
from handlers.admin.update_item import router as update_item_router
from handlers.admin.delete_item import router as delete_item_router
from handlers.admin.delete_category import router as delete_category_router
from handlers.admin.post_category import router as post_category_router
from handlers.admin.update_category import router as update_category_router
from handlers.admin.post_cafe import router as post_cafe_router
from handlers.admin.update_cafe import router as update_cafe_router
from handlers.admin.delete_cafe import router as delete_cafe_router
from handlers.admin.delete_order import router as delete_order_router
from handlers.admin.post_locale import router as post_locale_router
from handlers.admin.delete_locale import router as delete_locale_router
from handlers.user.user import router as user_router
from handlers.user.order import router as order_router
from handlers.user.dest import router as dest_router
from handlers.group import router as group_router
from database.engine import create_db, drop_db
from aiogram.types import BotCommandScopeAllPrivateChats

bot=Bot(token=getenv('TOKEN'),default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher()
dp.include_routers(
    admin_router,post_category_router,update_category_router,delete_item_router,delete_category_router,
    post_item_router,update_item_router,post_cafe_router,update_cafe_router,delete_cafe_router,
    order_router,user_router,group_router,dest_router,post_locale_router,delete_locale_router,delete_order_router
    )
bot.admins=[]

async def on_startup(bot):
#    param=False
#    if param:
#    await drop_db()
    await create_db()
    
async def on_shutdown(bot):
    print('bot is down')

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=['messages','edited_messages'])
    
if __name__=='__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')


