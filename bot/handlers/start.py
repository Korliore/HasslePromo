from aiogram import Router, types
from aiogram.filters import Command
from bot.db import db
import os
from aiogram.types import ChatJoinRequest
from aiogram.types.input_file import FSInputFile
import asyncio

router = Router()


async def get_menu_data(user_id: int):
    row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", user_id)
    quest_lvl = row["quest_lvl"] if row else None
    photo = None

    if quest_lvl == 1:
        text = (
            "👋 Привет! Я помогу тебе легко заработать!!\n\n"
            "💸 Хочешь получить <b>200₽</b> за пару минут? Тогда лови условия:\n\n"
            "1️⃣ <b>Зарегистрируйся по ссылке: https://hassle.online/ref/telega</b>\n"
            "2️⃣ <b>Пришли мне скриншот своей регистрации!</b>\n\n"
            "<i>Проверяем мгновенно! Действуй!</i>\n\n"
            "📌 <b>ЗАПОМНИ ДАННЫЕ от АККАУНТА!! ПРИГОДИТСЯ ДЛЯ ПРОВЕРКИ!!</b>"
        )
    else:
        text = (
            "😳 Ох, ты хочешь в сумме заработать 600 рублей? Ну держи!!\n\n"
            "<b>📌 Условия:</b>\n"
            "<blockquote>"
            "- Скачать игру Hassle Online // Radmir RP (ссылки внизу)\n\n"
            "- Прокачать в игре 3 уровень\n\n"
            "- Получить права и телефон\n\n"
            "- Ввести команду <code>/pcode</code> и <code>#gang</code> <b>НА 8 СЕРВЕРЕ</b>\n"
            "</blockquote>\n"
            "<b>📢 После этого нужно написать нашему менеджеру:</b> @vladimiras01\n\n"
            "📥 Он проверит и выплатит деньги, только скинь ему скриншоты выполнения условий\n\n"
            "📲 Скачать игру на Android: <a href='https://play.google.com/store/apps/details?id=com.hassle.online'>Google Play</a> (тык)\n"
            "📺 Скачать игру на iOS: <a href='https://apps.apple.com/us/app/hassle-online/id1624507378?l=ru'>App Store</a> (тык)\n"
            "💻 Скачать игру на ПК: <a href='https://radmir.online/'>Radmir Online</a> (тык)\n\n"
            "Желаю удачи!\n\n"
            "<b>⭐ ОТЗЫВЫ О ВЫПЛАТАХ 600Р:</b>\n https://t.me/otz_br600\n\n"
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
    if photo:
        photo_file = FSInputFile(photo)
        await message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
        await message.answer("Меню", reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)


@router.chat_join_request()
async def handle_join_request(event: ChatJoinRequest):
    # Добавляем пользователя в БД
    await db.execute(
        "INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        event.from_user.id,
        event.from_user.username
    )

    await asyncio.sleep(2)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="ДА", callback_data="menu"),
            ]
        ]
    )
    try:
        await event.bot.send_message(
            event.from_user.id,
            "🤩 Привет!! Хочешь заработать 200₽ // 400 BC за пару секунд?\n\n Тогда жми кнопку 'ДА'",
            reply_markup=keyboard)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


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
            "https://t.me/br_otz\n\n"
            "🥳 Уже десятки людей получили свои деньги!! Чем ты хуже? Действуй!!"
        )
    else:
        text = (
            "Уже много людей получили от нас по 600р 👇👇\n\n"
            "https://t.me/otz_br600\n\n"
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
    await call.message.delete()

    text, keyboard, photo = await get_menu_data(call.from_user.id)
    if photo:
        from aiogram.types.input_file import FSInputFile
        photo_file = FSInputFile(photo)
        await call.message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
        await call.message.answer("Меню", reply_markup=keyboard)
    else:
        await call.message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)
