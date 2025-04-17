import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_broadcaster import Broadcaster

from bot.config import BOT_TOKEN
from bot.db import db
from bot.models import CREATE_USERS_TABLE, CREATE_SCREENSHOTS_TABLE
from bot.utils.vk_ocr import VKService
from bot.handlers import start, screenshot, payout, admin

async def on_startup():
    await db.connect()
    await db.execute(CREATE_USERS_TABLE)
    await db.execute(CREATE_SCREENSHOTS_TABLE)

async def on_shutdown(vk_service: VKService):
    await db.close()
    await vk_service.close()

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Создаём OCR‑сервис и кладём в контекст
    vk_service = await VKService.create()
    dp["vk_service_ocr"] = vk_service

    # Регистрируем хендлеры
    dp.include_router(start.router)
    dp.include_router(screenshot.router)
    dp.include_router(payout.router)
    dp.include_router(admin.router)

    broadcaster = Broadcaster(bot)
    broadcaster.setup(dispatcher=dp)

    await on_startup()
    print("Бот запущен!", flush=True)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(vk_service)

if __name__ == "__main__":
    asyncio.run(main())
