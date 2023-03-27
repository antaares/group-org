from aiogram import types
from aiogram.dispatcher.filters import Text
from loader import dp, db, bot

from filters import IsAdmin
from filters import IsPrivate

from keyboards.default.adminKeys import ADMIN_MENU

@dp.message_handler(IsPrivate(), IsAdmin(), Text(equals="📈Statistika📉"), state="*")
async def SendStat(message: types.Message):
    users = len(db.all())
    text = f"Foydalanuvchilar: {users} ta"
    await message.answer(text=text)