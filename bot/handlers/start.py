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
            "👋 Привет! Я помогу тебе легко заработать!!\n\n"
            "💸 Хочешь получить <b>200₽</b> за пару минут? Тогда лови условия:\n\n"
            "1️⃣ Зарегистрируйся по ссылке: https://hassle.online/ref/telega\n\n"
            "2️⃣ Пришли мне скриншот своей регистрации!\n\n"
            "<i>Проверяем мгновенно! Действуй!</i>"
        )
    else:
        text = (
            "😳 Ох, ты хочешь в сумме заработать 600 рублей? Ну держи!!\n\n"
            "<b>📌 Условия:</b>\n"
            "<blockquote>"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду /pcode и #telega на ЛЮБОМ сервере\n"
            "</blockquote>\n"
            "<b>📢 После этого нужно написать нашему менеджеру:</b> @vladimiras01\n\n"
            "📥 Он проверит и выплатит деньги, только скинь ему  скриншоты выполнения условий\n\n"
            "📲 Скачать игру на Android: <a href='[https://play.google.com/store/apps/details?id=com.hassle.online'>Google](https://play.google.com/store/apps/details?id=com.hassle.online'>Google) Play</a> (тык)\n"
            "📺 Скачать игру на iOS: <a href='[https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App](https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App) Store</a> (тык)\n"
            "💻 Скачать игру на ПК: <a href='[https://radmir.online/'>Radmir](https://radmir.online/'>Radmir) Online</a> (тык)\n\n"
            "Желаю удачи!"
        )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
            ]
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
    text = ("Наши отзывы ты можешь посмотреть по ссылке 👇👇\n\n"
            "https://t.me/br_otz\n\n"
            "🥳 Уже десятки людей получили свои деньги!! Чем ты хуже? Действуй!!")
    await call.message.answer(text, reply_markup=menu_keyboard)

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
            "👋 Привет! Я помогу тебе легко заработать!!\n\n"
            "💸 Хочешь получить <b>200₽</b> за пару минут? Тогда лови условия:\n\n"
            "1️⃣ Зарегистрируйся по ссылке: https://hassle.online/ref/telega\n\n"
            "2️⃣ Пришли мне скриншот своей регистрации!\n\n"
            "<i>Проверяем мгновенно! Действуй!</i>"
        )
    else:
        text = (
            "😳 Ох, ты хочешь в сумме заработать 600 рублей? Ну держи!!\n\n"
            "<b>📌 Условия:</b>\n"
            "<blockquote>"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду /pcode и #telega на ЛЮБОМ сервере\n"
            "</blockquote>\n"
            "<b>📢 После этого нужно написать нашему менеджеру:</b> @vladimiras01\n\n"
            "📥 Он проверит и выплатит деньги, только скинь ему  скриншоты выполнения условий\n\n"
            "📲 Скачать игру на Android: <a href='[https://play.google.com/store/apps/details?id=com.hassle.online'>Google](https://play.google.com/store/apps/details?id=com.hassle.online'>Google) Play</a> (тык)\n"
            "📺 Скачать игру на iOS: <a href='[https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App](https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App) Store</a> (тык)\n"
            "💻 Скачать игру на ПК: <a href='[https://radmir.online/'>Radmir](https://radmir.online/'>Radmir) Online</a> (тык)\n\n"
            "Желаю удачи!"
        )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
            ]
        ]
    )
    await call.message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)