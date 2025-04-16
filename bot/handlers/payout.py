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
        await call.message.answer("Ты еще не выполнил все условия! Прочитай внимательно", reply_markup=menu_keyboard)
        return
    elif user["balance"] < 500:
        menu_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Получить", callback_data="menu")]
            ]
        )
        
        await call.message.answer(
            "К сожалению выплаты производятся только от 500 рублей. Но у меня хорошая новость!! Ты можешь получить еще 400 рублей. Нажми 'ПОЛУЧИТЬ'",
            reply_markup=menu_keyboard
        )
        
        row = await db.fetchrow("SELECT quest_lvl FROM users WHERE telegram_id = $1", call.from_user.id)
        quest_lvl = row["quest_lvl"] if row else None
        if quest_lvl <=1:
            await db.execute("UPDATE users SET quest_lvl = quest_lvl + 1 WHERE telegram_id = $1", call.from_user.id)
        return
    else:
        await call.message.answer("Пиши менеджеру для выплаты!", show_alert=True)