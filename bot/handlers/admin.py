from datetime import datetime
from aiogram import Router, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from bot.db import db
from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import TextContent
from aiogram import F
from bot.config import LOG_CHAT_ID

router = Router()

class BroadcastState(StatesGroup):
    broadcast_text = State()

@router.message(Command("stats"))
async def stats(message: types.Message):
    if str(message.chat.id) != LOG_CHAT_ID:
        return

    parts = message.text.split()
    if len(parts) == 2:
        date_str = parts[1]
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            await message.answer("Неверный формат даты. Используйте YYYY-MM-DD.")
            return
        
        count = await db.fetchrow("SELECT COUNT(*) FROM users WHERE registered_at::date = $1::date", date)
        valid = await db.fetchrow("SELECT COUNT(*) FROM users WHERE registered_at::date = $1::date AND has_sent_screenshot = True", date)
        await message.answer(f"Пользователей за {date}: {count['count']}\nВалидных скриншотов: {valid['count']}")
    else:
        total = (await db.fetchrow("SELECT COUNT(*) FROM users"))['count']
        valid = (await db.fetchrow("SELECT COUNT(*) FROM users WHERE has_sent_screenshot = True"))['count']
        await message.answer(f"Всего пользователей: {total}\nВалидных скриншотов: {valid}")

@router.message(Command("notify"))
async def broadcast_command_handler(msg: Message, state: FSMContext):
    if str(msg.chat.id) != LOG_CHAT_ID:
        return
    # Создаем клавиатуру с кнопкой отмены
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
    ])
    
    await msg.answer(
        'Введите текст для рассылки:', 
        reply_markup=keyboard
    )
    await state.set_state(BroadcastState.broadcast_text)

# Хэндлер для отмены через кнопку
@router.callback_query(F.data == "cancel_broadcast", BroadcastState.broadcast_text)
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Рассылка отменена")
    await callback.answer()

@router.message(StateFilter(BroadcastState.broadcast_text))
async def start_broadcast(
    msg: Message, 
    state: FSMContext,
    broadcaster: Broadcaster
):
    if str(msg.chat.id) != LOG_CHAT_ID:
        return
    await state.clear()
    
    users = await db.fetch("SELECT telegram_id FROM users")
    user_ids = [user['telegram_id'] for user in users]
    
    content = TextContent(text=msg.text)  # Теперь импорт корректен
    
    mailer = await broadcaster.create_mailer(chats=user_ids, content=content)
    mailer.start()
    
    await msg.answer(f"Рассылка начата для {len(user_ids)} пользователей.")

@router.message(Command("help"))
async def admin_help(
    msg: Message
):
    if str(msg.chat.id) != LOG_CHAT_ID:
        return
    await msg.answer("/stats - получить стату за все время\n/stats 2025-10-11 - получить стату за конкретную дату.\n/notify - панель рассылки")
