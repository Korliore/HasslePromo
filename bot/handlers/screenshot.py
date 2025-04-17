from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from bot.config import LOG_CHAT_ID
from bot.db import db
from aiogram.enums import ChatType
from bot.utils.vk_ocr import VKService  # добавь импорт, если его не было

router = Router()

REQUIRED_TEXTS = ["регистрация", "пройдена", "успешно", "удачной", "начать", "игру"]
REQUIRED_COLOR = (30, 237, 130)

@router.message(F.photo, F.chat.type == ChatType.PRIVATE)
async def handle_screenshot(message: types.Message, bot: Bot, **data):
    # Удаляем все последние сообщения пользователя (фото, текст и т.д.)
    ok_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Меню", callback_data="menu")]
        ]
    )
    # получение отправлял ли скрин юзер
    user = await db.fetchrow("SELECT balance, has_sent_screenshot FROM users WHERE telegram_id = $1", message.from_user.id)
    if not user or user["has_sent_screenshot"]:
        await message.answer("Ты уже отправил скриншот!", reply_markup=ok_keyboard)
        # return # для теста
    
    file = await bot.get_file(message.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)
    file_bytes = file_bytes.read()
    vk_service_ocr: VKService = data["vk_service_ocr"]

    img_text = await vk_service_ocr.recognize_text(file_bytes, 'screenshot.jpg')
    await message.answer(f"Отлично! Распознаный текст. {img_text}")

    # await db.execute(
    #     "INSERT INTO screenshots (user_id, file_id) VALUES ($1, $2)",
    #     message.from_user.id, message.photo[-1].file_id
    # )
    # if is_valid:
    #     await db.execute(
    #         "UPDATE users SET balance = balance + 200, has_sent_screenshot = TRUE WHERE telegram_id = $1",
    #         message.from_user.id
    #     )
    #     await message.answer("Отлично! Ты выполнил условия! На твой баланс добавлено 200 рублей!", reply_markup=ok_keyboard)
    # else:
    #     await message.answer("Мы не смогли проверить твой скриншот. Попробуй прислать другое изображение!", reply_markup=ok_keyboard)
    #
    # valid_str = "Да" if is_valid else "Нет"
    # # Отправка скрина лог-чату
    # await bot.send_photo(LOG_CHAT_ID, message.photo[-1].file_id,
    #                      caption=f"Скриншот от @{message.from_user.username or message.from_user.id}. Валидный: {valid_str}")



@router.callback_query(lambda c: c.data == "ok_screenshot")
async def ok_screenshot_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()