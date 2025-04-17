from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from bot.config import LOG_CHAT_ID
from bot.db import db
from aiogram.enums import ChatType
from bot.utils.vk_ocr import VKService  # добавь импорт, если его не было
from aiogram.types import InputMediaPhoto

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
    user = await db.fetchrow("SELECT balance, has_sent_screenshot FROM users WHERE telegram_id = $1",
                             message.from_user.id)
    if not user or user["has_sent_screenshot"]:
        await message.answer("Ты уже отправил скриншот!", reply_markup=ok_keyboard)
        # return # для теста

    file = await bot.get_file(message.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)
    file_bytes = file_bytes.read()
    vk_service_ocr: VKService = data["vk_service_ocr"]

    f = await bot.get_file(message.photo[-1].file_id)
    data_bytes = (await bot.download_file(f.file_path)).read()

    img_text = await vk_service_ocr.recognize_text(data_bytes)

    is_valid = await vk_service_ocr.validate_screen(img_text)

    if is_valid:
        # await db.execute(
        #     "UPDATE users SET balance = balance + 200, has_sent_screenshot = TRUE WHERE telegram_id = $1",
        #     message.from_user.id
        # )
        await message.answer("Отлично! Ты выполнил условия! На твой баланс добавлено 200 рублей!",
                             reply_markup=ok_keyboard)
    else:
        EXAMPLE_PHOTO_IDS = [
            "AgACAgIAAxkBAAOZaAECryMjEo8LpxUNXmVJ9kChevcAAl7xMRvA7glIw8YbkfwGHfsBAAMCAAN5AAM2BA",
            "AgACAgIAAxkBAAObaAEDAAFLj1Kwdu8skN4LNgxrOJReAAJj8TEbwO4JSPeRvB7BAAF3dAEAAwIAA3kAAzYE"
        ]
        media = [
            InputMediaPhoto(
                media=EXAMPLE_PHOTO_IDS[0],
            ),
            InputMediaPhoto(
                media=EXAMPLE_PHOTO_IDS[1],
            )
        ]

        await bot.send_media_group(
            chat_id=message.from_user.id,
            media=media,
        )
        await message.answer("Нам не удалось проверить твою регистрацию. Пожалуйста, обрати внимание на примеры и отправь новый скриншот.", reply_markup=ok_keyboard)
    valid_str = "Да" if is_valid else "Нет"
    # Отправка скрина лог-чату
    await bot.send_photo(LOG_CHAT_ID, message.photo[-1].file_id,
                         caption=f"Скриншот от @{message.from_user.username or message.from_user.id}. Валидный: {valid_str}.\n{message.photo[-1].file_id}")


@router.callback_query(lambda c: c.data == "ok_screenshot")
async def ok_screenshot_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
