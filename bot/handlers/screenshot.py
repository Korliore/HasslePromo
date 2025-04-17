from aiogram import Router, types, F
from aiogram.filters import Command
from bot.config import LOG_CHAT_ID
from bot.db import db
from bot.utils.ocr import analyze_screenshot
from aiogram.enums import ChatType

router = Router()

REQUIRED_TEXTS = ["регистрация", "пройдена", "успешно", "удачной", "начать", "игру"]
REQUIRED_COLOR = (30, 237, 130)

@router.message(F.photo, F.chat.type == ChatType.PRIVATE)
async def handle_screenshot(message: types.Message, bot):
    # Удаляем все последние сообщения пользователя (фото, текст и т.д.)
    try:
        history = await bot.get_chat_history(message.chat.id, limit=20)
        for msg in history:
            if msg.from_user and msg.from_user.id == message.from_user.id:
                try:
                    await bot.delete_message(message.chat.id, msg.message_id)
                except Exception:
                    pass
    except Exception:
        pass
    ok_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    # получение баланса юзера
    user = await db.fetchrow("SELECT balance, has_sent_screenshot FROM users WHERE telegram_id = $1", message.from_user.id)
    if not user or user["has_sent_screenshot"]:
        await message.answer("Ты уже отправил скриншот!", reply_markup=ok_keyboard)
        return
    
    file = await bot.get_file(message.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)
    file_bytes = file_bytes.read()

    is_valid = await analyze_screenshot(file_bytes, REQUIRED_TEXTS, REQUIRED_COLOR)

    await db.execute(
        "INSERT INTO screenshots (user_id, file_id) VALUES ($1, $2)",
        message.from_user.id, message.photo[-1].file_id
    )
    valid_str = "Да" if is_valid else "Нет"
    # Отправка скрина лог-чату
    await bot.send_photo(LOG_CHAT_ID, message.photo[-1].file_id,
                         caption=f"Скриншот от @{message.from_user.username or message.from_user.id}. Валидный: {valid_str}") 

    
    if is_valid:
        await db.execute(
            "UPDATE users SET balance = balance + 200, has_sent_screenshot = TRUE WHERE telegram_id = $1",
            message.from_user.id 
        )
        await message.answer("Отлично! Ты выполнил условия! На твой баланс добавлено 200 рублей!", reply_markup=ok_keyboard)
    else:
        await message.answer("Мы не смогли проверить твой скриншот. Попробуй прислать другое изображение!", reply_markup=ok_keyboard)

@router.callback_query(lambda c: c.data == "ok_screenshot")
async def ok_screenshot_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()