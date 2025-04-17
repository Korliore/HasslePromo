from aiogram import Router, types
from aiogram.filters import Command
from bot.db import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.execute(
        "INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        message.from_user.id, message.from_user.username
    )

    row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", message.from_user.id)
    quest_lvl = row["quest_lvl"] if row else None
    if quest_lvl == 1:
        text = (
    "👋 <b>Привет!</b> Я — твой помощник по легким заработкам в Hassle Online!\n\n"
    "💸 Хочешь получить <b>200₽</b> за пару минут? Тогда лови условия:\n\n"
    "1️⃣ <b>Зарегистрируйся</b> по ссылке: <a href='https://hassle.online/ref/telega'>https://hassle.online/ref/telega</a>\n"
    "2️⃣ <b>Пришли мне скриншот</b> своей регистрации!\n\n"
)
    else:
        text = (
            "👋 <b>Ох, ты хочешь в сумме заработать 600 рублей?</b> Хорошо.\n\n"
            "Условия:\n\n"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду /pcode и #telega на ЛЮБОМ сервере\n\n"
            "После этого нужно написать нашему менеджеру: @vladimiras01\n"
            "Он проверит и выплатит деньги, только скинь ему  скриншоты выполнения условий.\n\n"
            "Скачать игру на Android: <a href='https://play.google.com/store/apps/details?id=com.hassle.online'>Google Play</a>\n"
            "Скачать игру на iOS: <a href='https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App Store</a>\n"
            "Скачать игру на ПК: <a href='https://radmir.online/'>Radmir Online</a>\n"
            "Желаю удачи!"
        )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
            ],
            [types.InlineKeyboardButton(text="Помощь", callback_data="help_screen")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)
    
@router.callback_query(lambda c: c.data == "reviews")
async def reviews_callback(call: types.CallbackQuery):
    await call.answer()
    # Удалить исходное сообщение
    await call.message.delete()
    menu_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    await call.message.answer("Вот ссылка на канал с отзывами: https://t.me/br_otz", reply_markup=menu_keyboard)

@router.callback_query(lambda c: c.data == "balance")
async def balance_callback(call: types.CallbackQuery):
    user = await db.fetchrow("SELECT balance FROM users WHERE telegram_id = $1", call.from_user.id)
    value = user["balance"] if user else 0
    await call.answer()
    # Удалить исходное сообщение
    await call.message.delete()
    menu_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    await call.message.answer(f"Твой баланс: {value}₽.", reply_markup=menu_keyboard)

@router.callback_query(lambda c: c.data == "menu")
async def menu_callback(call: types.CallbackQuery):
    await call.answer()
    # Удалить текущее сообщение (например, окно Баланс или Отзывы)
    await call.message.delete()
    row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", call.from_user.id)
    quest_lvl = row["quest_lvl"] if row else None
    if quest_lvl == 1:
        text = (
    "👋 <b>Привет!</b> Я — твой помощник по легким заработкам в Hassle Online!\n\n"
    "💸 Хочешь получить <b>200₽</b> за пару минут? Тогда лови условия:\n\n"
    "1️⃣ <b>Зарегистрируйся</b> по ссылке: <a href='https://hassle.online/ref/telega'>https://hassle.online/ref/telega</a>\n"
    "2️⃣ <b>Пришли мне скриншот</b> своей регистрации!\n\n"
)
    else:
        text = (
            "👋 <b>Ох, ты хочешь в сумме заработать 600 рублей?</b> Хорошо.\n\n"
            "Условия:\n\n"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду /pcode и #telega на ЛЮБОМ сервере\n\n"
            "После этого нужно написать нашему менеджеру: @vladimiras01\n"
            "Он проверит и выплатит деньги, только скинь ему  скриншоты выполнения условий.\n\n"
            "Скачать игру на Android: <a href='https://play.google.com/store/apps/details?id=com.hassle.online'>Google Play</a>\n"
            "Скачать игру на iOS: <a href='https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App Store</a>\n"
            "Скачать игру на ПК: <a href='https://radmir.online/'>Radmir Online</a>\n"
            "Желаю удачи!"
        )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
            ],
            [types.InlineKeyboardButton(text="Помощь", callback_data="help_screen")]
        ]
    )
    await call.message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)