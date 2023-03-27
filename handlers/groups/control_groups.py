import asyncio
import datetime
import re

import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup
from filters.is_admin import IsChatAdmin
from filters.is_group import BlackWord
from loader import dp, bot, db


# /ro oki !ro (read-only) komandalari uchun handler
# foydalanuvchini read-only ya'ni faqat o'qish rejimiga o'tkazib qo'yamiz.
@dp.message_handler(IsGroup(), IsChatAdmin(), Command("ro", prefixes="!/"), is_reply=True)
async def read_only_mode(message: types.Message):
    print(message.text)
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    command_parse = re.compile(r"(!ro|/ro) ?(\d+)? ?([\w+\D]+)?")
    parsed = command_parse.match(message.text)
    time = parsed.group(2)
    comment = parsed.group(3)
    if not time:
        time = 5

    

    time = int(time)

    # Ban vaqtini hisoblaymiz (hozirgi vaqt + n minut)
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    try:
        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        await message.reply_to_message.delete()
    except aiogram.utils.exceptions.BadRequest as err:
        await message.answer(f"Xatolik! {err.args}")
        return

    # Пишем в чат
    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} {time} minut yozish huquqidan mahrum qilindi.\n"
                         f"Sabab: \n<b>{comment}</b>")

    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
    # 5 sekun kutib xabarlarni o'chirib tashlaymiz
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()

# read-only holatdan qayta tiklaymiz
@dp.message_handler(IsGroup(), IsChatAdmin(), Command("unro", prefixes="!/"))
async def undo_read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id

    user_allowed = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
        can_change_info=False,
        can_pin_messages=False,
    )
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)
    await message.chat.restrict(user_id=member_id, permissions=user_allowed, until_date=0)
    await message.reply(f"Foydalanuvchi {member.full_name} tiklandi")

    # xabarlarni o'chiramiz
    await message.delete()
    await service_message.delete()

# Foydalanuvchini banga yuborish (guruhdan haydash)
@dp.message_handler(IsGroup(),  IsChatAdmin(),Command("ban", prefixes="!/"))
async def ban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    await message.chat.kick(user_id=member_id)

    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} guruhdan haydaldi")
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()

# Foydalanuvchini bandan chiqarish, foydalanuvchini guruhga qo'sha olmaymiz (o'zi qo'shilishi mumkin)
@dp.message_handler(IsGroup(), IsChatAdmin(), Command("unban", prefixes="!/"))
async def unban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    await message.chat.unban(user_id=member_id)
    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} bandan chiqarildi")
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)

    await message.delete()
    await service_message.delete()



# the handler for save word to black list
@dp.message_handler(IsGroup(),  IsChatAdmin(), Command("addword", prefixes="!/"))
async def add_word(message: types.Message):
    args = message.get_args().split()
    if not args:
        await message.answer("So'zni kiriting! Namuna: /addword reklama")
        return
    for word in args:
        db.add_black_word(word = word.lower().replace(",", ""),chat_id = message.chat.id)
    await message.answer("So'zlar qora ro'yxatga qo'shildi!")


# the handler for delete word from black list
@dp.message_handler(IsGroup(), IsChatAdmin(), Command("delword", prefixes="!/"))
async def del_word(message: types.Message):
    args = message.get_args().split()
    if not args:
        await message.answer("So'zni kiriting! Namuna: /delword reklama")
        return
    for word in args:
        db.delete_black_word(message.chat.id, word=word.lower().replace(",", ""))
    await message.answer("So'zlar qora ro'yxatdan o'chirildi!")


# the handler for delete all word from black list
@dp.message_handler(IsGroup(), IsChatAdmin(), Command("clear", prefixes="!/"))
async def clear_words(message: types.Message):
    db.delete_black_words(message.chat.id)
    await message.answer("Qora ro'yxat tozalandi!")



@dp.message_handler(IsGroup(),content_types=types.ContentType.ANY,)
async def read_only_mode(message: types.Message):
    me_ = await bot.get_me()
    member = await bot.get_chat_member(message.chat.id,me_.id)
    if member.is_chat_admin() == False:
        await message.answer("Guruhda admin emasman, ishlamayman!")
        return
    is_black = False
    if message.text and " " in message.text:
        for word in message.text.lower().split():
            black_words = db.get_black_list(message.chat.id) or []
            if word in black_words:
                is_black = True
                break
    elif message.text:
        word = message.text.lower()
        black_words = db.get_black_list(message.chat.id) or []
        if word in black_words:
            is_black = True


    if is_black == False:
        return
    member = message.from_user
    member_id = member.id
    await message.reply(f"{member.get_mention(as_html=True)} sizning xabaringizda qora ro'yxatdagi so'z mavjud. Sizga yozish huquqi o'chirildi. \n")
    until_date = datetime.datetime.now() + datetime.timedelta(hours=4)
    await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
    await message.delete()