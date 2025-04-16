import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.db import db
from bot.models import CREATE_USERS_TABLE, CREATE_SCREENSHOTS_TABLE
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_broadcaster import Broadcaster

from bot.handlers import start, screenshot, payout, admin

async def on_startup():
    await db.connect()
    # Создание таблиц
    await db.execute(CREATE_USERS_TABLE)
    await db.execute(CREATE_SCREENSHOTS_TABLE)

async def on_shutdown():
    await db.close()

from aiogram import BaseMiddleware

class CleanChatMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if hasattr(event, 'chat') and hasattr(event, 'from_user'):
            bot = data.get('bot')
            if bot is not None:
                try:
                    history = await bot.get_chat_history(event.chat.id, limit=20)
                    for msg in history:
                        # Удаляем все сообщения кроме текущего
                        if msg.message_id != getattr(event, 'message_id', None):
                            try:
                                await bot.delete_message(event.chat.id, msg.message_id)
                            except Exception:
                                pass
                except Exception:
                    pass
        return await handler(event, data)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.message.middleware(CleanChatMiddleware())
    dp.callback_query.middleware(CleanChatMiddleware())
    dp.include_router(start.router)
    dp.include_router(screenshot.router)
    dp.include_router(payout.router)
    dp.include_router(admin.router)
    broadcaster = Broadcaster(bot)
    broadcaster.setup(dispatcher=dp)
    await on_startup()
    print('Бот запущен!', flush=True)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())