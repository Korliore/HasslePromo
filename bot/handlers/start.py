from aiogram import Router, types
from aiogram.filters import Command
from bot.db import db
import os
from aiogram.types import ChatJoinRequest
from aiogram.types.input_file import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from bot.utils.redis_provider import r
from bot.utils.captcha_generatot import gen_captcha
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bot.main import bot
router = Router()


async def get_menu_data(user_id: int):
    row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", user_id)
    quest_lvl = row["quest_lvl"] if row else None
    photo = None

    if quest_lvl == 1:
        text = (
            "😭 <b>К сожалению выплаты по 200 рублей закончились, но ты можешь получить 600 рублей!! Жми 'ХОЧУ'</b>"
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

    if quest_lvl == 1:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="ХОЧУ", callback_data="get_600"),]
            ]
        )
    else:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Выплата", callback_data="payout"),
                    types.InlineKeyboardButton(text="Отзывы", callback_data="reviews"),
                    types.InlineKeyboardButton(text="Баланс", callback_data="balance"),
                    types.InlineKeyboardButton(text="Получить аккаунт", callback_data="get_account"),
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

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Получить аккаунт", callback_data="get_account"),
                #types.InlineKeyboardButton(text="Получить 600 Р", callback_data="get_600_r"),
            ]
        ]
    )
    await message.answer("Меню", reply_markup=keyboard)

    # if photo:
    #     photo_file = FSInputFile(photo)
    #     await message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
    #     await message.answer("Меню", reply_markup=keyboard)

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
            "🤩 Привет!! Хочешь получить бесплатный аккаунт?\n\n Тогда жми кнопку 'ДА'",
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
    get_acc = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Получить аккаунт", callback_data="get_account")]
        ]
    )
    await call.message.answer("Меню", reply_markup=get_acc)

    # text, keyboard, photo = await get_menu_data(call.from_user.id)
    # if photo:
    #     from aiogram.types.input_file import FSInputFile
    #     photo_file = FSInputFile(photo)
    #     await call.message.answer_photo(photo=photo_file, caption=text, disable_web_page_preview=True)
    #     await call.message.answer("Меню", reply_markup=keyboard)
    # else:
    #     await call.message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)

@router.callback_query(lambda c: c.data == "get_600")
async def get_600_callback(call: types.CallbackQuery):
    await call.answer()
    # ставим типу 2 лвл и кидаем опять главное меню
    await db.execute("UPDATE users SET quest_lvl = 2, has_sent_screenshot = True WHERE telegram_id = $1", call.from_user.id)
    await menu_callback(call)

REQUIRED_CHANNELS = [
    "https://t.me/brnews09",
    "https://t.me/blackrussia_ry",
    "https://t.me/novostibr001",
]

CHANNEL_USERNAMES = [
    "novostibr001",
    "blackrussia_ry",
    "brnews09"
]


def get_subscription_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Подписаться", url=link)]
        for link in REQUIRED_CHANNELS
    ]
    buttons.append([InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subs")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def check_user_subscriptions(user_id: int) -> bool:
    for channel in CHANNEL_USERNAMES:
        try:
            member = await bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status not in ["member", "creator", "administrator"]:
                return False
        except TelegramBadRequest:
            return False
    return True

@router.callback_query(lambda c: c.data == "get_account")
async def get_account_callback(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer()
    is_subscribed = await check_user_subscriptions(call.from_user.id)
    if not is_subscribed:
        await call.message.answer(
            "🎉 Ты выбрал бесплатный аккаунта\n"
            "Отлично! Подпишись на наши каналы для получения данных от аккаунта\n",
            reply_markup=get_subscription_keyboard()
        )
        return

    # Рендерим капчу
    text, path = await gen_captcha()
    r.set(f"captcha:{call.from_user.id}", text, ex=300)  # хранится 5 мин
    await call.message.answer_photo(photo=FSInputFile(path),
                                    caption="🗨 <b>Введи капчу, чтоб получить аккаунт</b>",
                                    reply_markup=None)
    return

@router.message(lambda m: r.exists(f"captcha:{m.from_user.id}"))
async def captcha_verify(message: types.Message):
    key = f"captcha:{message.from_user.id}"
    real = r.get(key).decode()
    r.delete(key)
    if message.text.strip().upper() == real:
        # Всё норм, чел подписан — кидаем учётку
        username = r.get("current_username").decode()
        password = r.get("current_password").decode()
        server = r.get("current_server").decode()
        menu_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Обновить данные", callback_data="get_account")]
            ]
        )
        await message.answer(
            f"🤑 А вот и данные:\n"
            f"<b>👤 Ник: {username}\n</b>"
            f"<b>🔑 Пароль: {password}\n</b>"
            f"<b>🌐 Сервер: {server}\n\n</b>"
            f"🗨 ВНИМАНИЕ!  Каждый час с 59 минут по 00 минут каждого часа обновляются аккаунты!!\n"
            f"🫡 Если ник или пароль неправильные, значит аккаунт уже забрали. Но не переживай, у тебя 24 шанса в сутки. Возвращайся скорее!",
            reply_markup=menu_keyboard
        )
    else:
        text, path = await gen_captcha()
        r.set(f"captcha:{message.from_user.id}", text, ex=300)  # хранится 5 мин
        await message.answer_photo(photo=FSInputFile(path),
                                        caption="❌ Неправильный код. Попробуй ещё раз.",
                                        reply_markup=None)

@router.callback_query(lambda c: c.data == "check_subs")
async def recheck_subs(call: types.CallbackQuery):

    await call.answer()
    is_subscribed = await check_user_subscriptions(call.from_user.id)
    if not is_subscribed:
        await call.message.answer(
            "❌ Похоже, ты не подписан(а) на все наши каналы. Чтобы получить аккаунт, подпишись на:",
            reply_markup=get_subscription_keyboard()
        )
        return
    await get_account_callback(call)