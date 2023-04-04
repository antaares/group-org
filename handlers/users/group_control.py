import asyncio
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from keyboards.default.groups_control import BUTTTON_AUTO
from keyboards.default.main_menu import BUTTTON

from aiogram.dispatcher import FSMContext
from keyboards.inline.group_controls import MainMenuControl
from states.auto_advertising import AutoMessage



from utils.ad_sender import start_service, stop_service

from loader import dp, db, bot




@dp.message_handler(Text(equals="👥 Guruh nazorati"))
async def bot_start(message: types.Message):
    await message.answer("👇Tanlang:",
                            reply_markup=MainMenuControl)



# @dp.callback_query_handler(text_contains="group_list")
# async def group_list(query: types.CallbackQuery):
#     # db.get_groups()
#     await query.answer(cache_time=0)
#     await query.message.answer("👇Guruhlaringiz ro'yxati:", reply_markup=MainMenuControl)


@dp.callback_query_handler(text_contains="auto_advertising")
async def auto_advertising(query: types.CallbackQuery):
    await query.answer(cache_time=0)
    await query.message.answer("Guruhingizga siz belgilagan vaqtda sizni reklamangizni tashlab turish funktsiyasi:", reply_markup=BUTTTON_AUTO)



@dp.message_handler(Text(equals="📝 Reklama qo'shish"))
async def add_advertising(message: types.Message):
    data = db.get_user_job(user_id=message.from_user.id)
    if data:
        await message.answer("Sizda aktiv reklama mavjud! Reklamani o'chirishingiz kerak")
        return
    await message.answer("Reklama yuboring har qanday formatda yuborishingiz mumkin!")
    # db.add_advertising(message.text)
    await AutoMessage.GetAdvertisement.set()


@dp.message_handler(state=AutoMessage.GetAdvertisement)
async def get_advertising(message: types.Message, state: FSMContext):
    await message.answer("Reklamani guruhlaringizga har necha daqiqa vaqt ichida yuborishni belgilang:"\
                         "Minimal 30 daqiqa va maksimal 2880 daqiqa!")
    await state.update_data(message=message)

    # db.add_time(message.text)
    await AutoMessage.GetTime.set()



async def time_confirm(time):
    if time.isdigit():
        if int(time) >= 30 and int(time) <= 2880:
            return True
        else:
            return False
    else:
        return False



@dp.message_handler(state=AutoMessage.GetTime)
async def get_time(message: types.Message, state: FSMContext):
    if not await time_confirm(message.text):
        await message.answer("Siz noto'g'ri vaqt belgiladingiz! Iltimos 30 dan katta va 2880 dan kichik raqam kiriting!")
        return
    await message.answer(f"Reklama qo'shildi! Reklama har {message.text} daqiqa vaqt ichida guruhlaringizga yuboriladi!",
                         reply_markup=BUTTTON)
    data = await state.get_data()
    data = data['message']
    await start_service(data=data, user_id=message.from_user.id, delay_time=int(message.text))
    
    # db.add_time(message.text)
    await state.finish()


@dp.message_handler(Text(equals="❌ Reklama o'chirish"))
async def delete_advertising(message: types.Message):
    await stop_service(user_id=message.from_user.id)
    await message.answer("Reklama o'chirildi!", reply_markup=BUTTTON)


@dp.callback_query_handler(Text(equals='advertising'))
async def advertising(query: types.CallbackQuery):
    await query.answer(cache_time=0)
    await query.message.answer("Reklama yuboring, men barcha guruhlaringizga shu reklamani yuboraman:")
    await AutoMessage.zed.set()



@dp.message_handler(state=AutoMessage.zed)
async def send_advertising(message: types.Message, state: FSMContext):
    await send_copy(message)
    await message.answer("Reklama guruhlaringizga yuborildi!", reply_markup=BUTTTON)
    await state.finish()


@dp.callback_query_handler(text_contains="pin_advertising")
async def pin_advertising(query: types.CallbackQuery):
    await query.answer(cache_time=0)
    await query.message.answer(
        "Reklamani yuboring men uni guruhlaringizga pin qilib yuboraman."
    )
    await AutoMessage.red.set()



@dp.message_handler(state=AutoMessage.red)
async def send_pin_advertising(message: types.Message, state: FSMContext):
    await send_copy_pin(message)
    await message.answer("Reklama guruhlaringizga yuborildi!", reply_markup=BUTTTON)
    await state.finish()




async def send_copy(message: types.Message):
    all = db.get_groups_by_admin(user_id=message.from_user.id)
    for group in all:
        try:
            await message.copy_to(group)
            await asyncio.sleep(0.3)
        except Exception as e:
            print(e)



async def send_copy_pin(message: types.Message):
    all = db.get_groups_by_admin(user_id=message.from_user.id)
    for group in all:
        try:
            msg = await message.copy_to(group, reply_markup=message.reply_markup)
            await bot.pin_chat_message(group, msg.message_id)
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(0.3)