from aiogram import Router, types, F, Bot
from aiogram.enums import ChatType
from aiogram.types import InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import asyncio  # для отложенной отправки уведомления
from bot.utils.redis_provider import r

from bot.config import LOG_CHAT_ID, TIMER_TIME, EXAMPLE_IDS
from bot.db import db
from bot.utils.vk_ocr import VKService

timer_time = TIMER_TIME

router = Router()


class PayoutStates(StatesGroup):
    waiting_for_details = State()

REQUIRED_TEXTS = ["регистрация", "пройдена", "успешно", "удачной", "начать", "игру"]
REQUIRED_COLOR = (30, 237, 130)

@router.message(F.photo, F.chat.type == ChatType.PRIVATE)
async def handle_screenshot(message: types.Message, bot: Bot, state: FSMContext, **data):
    # получаем юзера из БД
    user = await db.fetchrow(
        "SELECT balance, has_sent_screenshot FROM users WHERE telegram_id = $1",
        message.from_user.id
    )
    if not user or user["has_sent_screenshot"]:
        await message.answer(
            "😔 Ты уже отправил скриншот!",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="Меню", callback_data="menu")]]
            )
        )
        return

    # скачиваем картинку и распознаём текст
    file = await bot.get_file(message.photo[-1].file_id)
    data_bytes = (await bot.download_file(file.file_path)).read()
    vk_ocr: VKService = data["vk_service_ocr"]
    img_text = await vk_ocr.recognize_text(data_bytes)
    is_valid = await vk_ocr.validate_screen(img_text)

    if is_valid:
        # начисляем баллы и отмечаем скрин принят
        await db.execute(
            "UPDATE users SET balance = balance + 200, has_sent_screenshot = TRUE WHERE telegram_id = $1",
            message.from_user.id
        )

        # просим реквизиты
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="Сменить реквизиты", callback_data="change_details")]]
        )
        await message.answer(
            "✅ Отлично! Ты можешь получить свою выплату!\n\n"
            "💳 Скинь номер карты, номер телефона, адрес кошелька криптовалюты. Ник и сервер куда донатим, либо иные данные для выплаты.\n\n"
            "📋 В любой момент ты можешь поменять реквизиты. <b>Жми на кнопку 'Сменить реквизиты'</b>",
            reply_markup=keyboard
        )
        await state.set_state(PayoutStates.waiting_for_details)
    else:
        # не прошёл проверку — кидаем примеры
        media = [InputMediaPhoto(media=pid) for pid in EXAMPLE_IDS]
        await bot.send_media_group(message.from_user.id, media)
        await message.answer(
            "😢 Не смогли проверить твой скрин. Смотри примеры и кидай новый.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="Меню", callback_data="menu")]]
            )
        )

    # логируем админам
    valid_str = "Да" if is_valid else "Нет"
    await bot.send_photo(
        LOG_CHAT_ID, message.photo[-1].file_id,
        caption=f"@{message.from_user.username or message.from_user.id} | Валидный: {valid_str}\n\nТекст: {img_text}"
    )

@router.callback_query(lambda c: c.data == "change_details")
async def change_details_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    user_id = call.from_user.id
    redis_key = f"payout:{user_id}"
    # удаляем ключ, чтобы таск ничего не отправил
    r.delete(redis_key)
    await call.message.answer("💰 Отправь свои реквизиты!")
    await state.set_state(PayoutStates.waiting_for_details)

@router.message(StateFilter(PayoutStates.waiting_for_details), F.chat.type == ChatType.PRIVATE)
async def handle_payout_details(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    redis_key = f"payout:{user_id}"

    # сохраняем реквизиты в БД
    await db.execute(
        "UPDATE users SET payout_details = $1 WHERE telegram_id = $2",
        message.text, user_id
    )
    # создаём ключ с TTL 60 сек
    r.set(redis_key, "1", ex=timer_time)

    await message.answer("✅ Мы получили твои реквизиты! Ожидай выплату в течении пары минут.")
    # запускаем таск, который через минуту проверит ключ
    asyncio.create_task(notify_min_payout_limit(user_id, message.bot))
    await state.clear()

async def notify_min_payout_limit(user_id: int, bot: Bot):
    await asyncio.sleep(timer_time - 1)
    redis_key = f"payout:{user_id}"
    exists = r.exists(redis_key)
    if exists:
        row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", user_id)
        quest_lvl = row["quest_lvl"] if row else None
        if quest_lvl <=1:
            await db.execute("UPDATE users SET quest_lvl = quest_lvl + 1 WHERE telegram_id = $1", user_id)
        await bot.send_message(
            user_id,
            "🙁 Платёжная система тормозит выплаты до <b>500 ₽</b>\n\n"
            "Но я знаю, как тебе получить целых 600₽! Жми 'ПОЛУЧИТЬ'.", 
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="Получить", callback_data="menu")]]
            )
        )
        # чистим ключ, чтобы не спамить
        r.delete(redis_key)
