from aiogram import Router, types
from bot.db import db
from aiogram import F

router = Router()

@router.callback_query(F.data.startswith('payout'))
async def payout_callback(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer()
    user = await db.fetchrow("SELECT balance, has_sent_screenshot FROM users WHERE telegram_id = $1", call.from_user.id)
    if not user or not user["has_sent_screenshot"]:
        menu_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Ок", callback_data="menu")]
            ]
        )
        text = (
            "<b>Ты еще не выполнил все условия!</b>\n\n"
            "1. Зарегистрируйся по ссылке https://hassle.online/ref/brt\n\n"
            "2. Пришли мне скриншот регистрации\n\n"
            "И получай свои денежки!!"
        )
        await call.message.answer(text, reply_markup=menu_keyboard)
        return
    elif user["balance"] < 750:
        menu_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Получить", callback_data="menu")]
            ]
        )
        text = (
            "🙁 Платежная система ограничила выплаты от <b>750 рублей</b>\n\n"
            "<b>Но я знаю как тебе получить целых 1500!!!</b>\n\n"
            "Нажми 'ПОЛУЧИТЬ'"
        )
        await call.message.answer(
            text,
            reply_markup=menu_keyboard
        )
        
        row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", call.from_user.id)
        quest_lvl = row["quest_lvl"] if row else None
        if quest_lvl <=1:
            await db.execute("UPDATE users SET quest_lvl = quest_lvl + 1 WHERE telegram_id = $1", call.from_user.id)
        return
    else:
        await call.message.answer("Пиши менеджеру для выплаты!", show_alert=True)