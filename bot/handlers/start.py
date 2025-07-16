from aiogram import Router, types
from aiogram.filters import Command
from asyncpg import Record

from bot.db import db
import os
from aiogram.types import (
    ChatJoinRequest,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.types.input_file import FSInputFile
import asyncio
from aiogram.exceptions import TelegramForbiddenError
from aiogram import F
import logging

logger = logging.getLogger(__name__)


router = Router()


async def get_menu_data(user_id: int):
    row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", user_id)
    quest_lvl = row["quest_lvl"] if row else None
    photo = None

    if quest_lvl == 1:
        text = (
            "👋 Привет! Я помогу тебе легко заработать!!\n\n"
            "💸 Хочешь получить <b>500₽</b> за пару минут? Тогда лови условия:\n\n"
            "1️⃣ <b>Зарегистрируйся по ссылке: https://hassle.online/ref/brt</b>\n"
            "2️⃣ <b>Пришли мне скриншот своей регистрации!</b>\n\n"
            "<i>Проверяем мгновенно! Действуй!</i>\n\n"
            "📌 <b>ЗАПОМНИ ДАННЫЕ от АККАУНТА!! ПРИГОДИТСЯ ДЛЯ ПРОВЕРКИ!!</b>"
        )
    else:
        text = (
            "😳 Ох, ты хочешь в сумме заработать 1500 рублей? Ну держи!!\n\n"
            "<b>📌 Условия:</b>\n"
            "<blockquote>"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду <code>/pcode</code> и <code>#brt</code> <b>НА 11 СЕРВЕРЕ</b>\n"
            "</blockquote>\n"
            "<b>📢 После этого нужно написать нашему менеджеру:</b> @vladimiras01\n\n"
            "📥 Он проверит и выплатит деньги, только скинь ему скриншоты выполнения условий\n\n"
            "📲 Скачать игру на Android: <a href='https://play.google.com/store/apps/details?id=com.hassle.online'>Google Play</a> (тык)\n"
            "📺 Скачать игру на iOS: <a href='https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App Store</a> (тык)\n"
            "💻 Скачать игру на ПК: <a href='https://radmir.online/'>Radmir Online</a> (тык)\n\n"
            "Желаю удачи!\n\n"
            "<b>⭐ ОТЗЫВЫ О ВЫПЛАТАХ:</b>\n https://t.me/+GimERJp3oEszY2Zi\n\n"
            "✅ Можно использовать аккаунт который ты регистрировал"
        )
        photo = os.path.join(os.path.dirname(__file__), '..', 'img', 'sber.jpg')

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
            ]
        ]
    )

    return text, keyboard, photo


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.execute(
        "INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        message.from_user.id, message.from_user.username
    )

    text, keyboard, photo = await get_menu_data(message.from_user.id)
    msg = await message.answer(
        ".",
        reply_markup=ReplyKeyboardRemove(),
    )
    # удалить сообщение
    await msg.delete()


    if photo:
        photo_file = FSInputFile(photo)
        await message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
        await message.answer("Меню", reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)


@router.message(F.text.lower() == "да")
async def handle_yes_message(message: types.Message):
    await cmd_start(message)


async def handle_join_request(event: ChatJoinRequest):
    user_id = event.from_user.id
    username = event.from_user.username or "без_юзернейма"

    # Проверим есть ли уже такой юзер в базе
    existing_user: Record | None = await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1", user_id
    )

    if existing_user:
        logger.info(f"👀 Юзер уже есть в БД: @{username} ({user_id})")
    else:
        await db.execute(
            "INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id,
            username
        )
        logger.info(f"🆕 Добавил нового юзера в БД: @{username} ({user_id})")

    await asyncio.sleep(5)

    # Клава с кнопкой "ДА"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ДА")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    try:
        await event.bot.send_message(
            chat_id=user_id,
            text="🤩 Привет!! Хочешь заработать 500₽ за пару секунд?\n\n Тогда жми кнопку 'ДА'",
            reply_markup=keyboard
        )
        logger.info(f"✅ Успешно отправил сообщение юзеру: @{username} ({user_id})")

    except TelegramForbiddenError as e:
        logger.warning(f"🚫 Forbidden! Не смог написать юзеру: @{username} ({user_id}) — {e}")

    except Exception as e:
        logger.error(f"💥 Ошибка при отправке сообщения @{username} ({user_id}): {e}")


@router.callback_query(lambda c: c.data == "reviews")
async def reviews_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()

    menu_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    user = await db.fetchrow("SELECT balance FROM users WHERE telegram_id = $1", call.from_user.id)
    value = user["balance"] if user else 0
    if value == 0:
        text = (
            "Наши отзывы ты можешь посмотреть по ссылке 👇👇\n\n"
            "https://t.me/+jDNOq4hCTG44MTli\n\n"
            "🥳 Уже десятки людей получили свои деньги!! Чем ты хуже? Действуй!!"
        )
    else:
        text = (
            "Уже много людей получили от нас выплаты 👇👇\n\n"
            "https://t.me/+GimERJp3oEszY2Zi\n\n"
            "Дерзай!!"
        )
    await call.message.answer(text, reply_markup=menu_keyboard)


@router.callback_query(lambda c: c.data == "balance")
async def balance_callback(call: types.CallbackQuery):
    user = await db.fetchrow("SELECT balance FROM users WHERE telegram_id = $1", call.from_user.id)
    value = user["balance"] if user else 0
    await call.answer()
    await call.message.delete()

    menu_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    await call.message.answer(
        f"🤩 Твой баланс: {value}₽.\n\nДля вывода денег перейди в раздел 'Выплата'",
        reply_markup=menu_keyboard
    )


@router.callback_query(lambda c: c.data == "menu")
async def menu_callback(call: types.CallbackQuery):
    await call.answer()
    text, keyboard, photo = await get_menu_data(call.from_user.id)
    if photo:
        photo_file = FSInputFile(photo)
        await call.message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
        await call.message.answer("Меню", reply_markup=keyboard)
    else:
        await call.message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)
    await call.message.delete()
