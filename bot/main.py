import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_broadcaster import Broadcaster
from bot.utils.redis_provider import r
from datetime import datetime, timedelta
import random
from bot.db import db
from bot.models import CREATE_USERS_TABLE, CREATE_SCREENSHOTS_TABLE
from bot.utils.vk_ocr import VKService
from bot.handlers import start, screenshot, payout, admin
from bot.utils.user_data_random import get_random_data
from bot.loader import bot

async def on_startup():
    await db.connect()
    await db.execute(CREATE_USERS_TABLE)
    await db.execute(CREATE_SCREENSHOTS_TABLE)

async def on_shutdown(vk_service: VKService):
    await db.close()
    await vk_service.close()


async def update_credentials():
    """Генерирует и сохраняет случайные учетные данные в Redis"""
    username, password, server = get_random_data()

    r.set("current_username", str(username))
    r.set("current_password", str(password))
    r.set("current_server", str(server))

    print(f"Обновлены учетные данные: {username}:{password}")

async def credentials_scheduler():
    """Запускает обновление учетных данных в последнюю минуту часа"""
    while True:
        now = datetime.now()
        # Вычисляем следующую 59-ю минуту
        next_run = now.replace(minute=59, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(hours=1)

        # Случайная задержка внутри минуты (0-59 секунд)
        delay = (next_run - now).total_seconds() + random.randint(0, 59)
        await asyncio.sleep(delay)

        await update_credentials()
        await asyncio.sleep(60)

async def main():
    dp = Dispatcher()
    await update_credentials()

    # Запускаем задачу обновления учетных данных в последнюю минуту часа
    asyncio.create_task(credentials_scheduler())
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
