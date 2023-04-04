from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from keyboards.inline.black_list import BLACK_LIST
from aiogram.dispatcher import FSMContext
from states.black_list_states import BlackList


from loader import dp




@dp.message_handler(Text(equals="📜 Qora ro'yxat"))
async def bot_start(message: types.Message):
    await message.answer("Qora ro'yxat har bir guruhda alohida ishlaydi:\n"\
                        "/addword qora ro'yxatga so'z qo'shish. (Namuna: /addword reklama)\n"\
                        "/delword qora ro'yxatdan so'z olib tashlash. (Namuna: /delword reklama)\n"\
                        "/clear qora ro'yxatni tozalash.")


    # await message.answer("👇Tanlang bo'limni barcha so'zlarni o'chirsangiz bu funktsiya o'chadi:",
    #                         reply_markup=BLACK_LIST)
    

@dp.callback_query_handler(text_contains="black_list_words")
async def black_list_words(query: types.CallbackQuery):
    await query.answer(cache_time=0)
    await query.message.answer("👇Barcha so'zlar:")




@dp.callback_query_handler(text_contains="black_list_add_word")
async def black_list_add_word(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=0)
    await query.message.answer("👇So'z qo'shish! Qora ro'yxat uchun so'z yuboring:")
    await BlackList.add_word.set()


@dp.message_handler(state=BlackList.add_word)
async def add_word(message: types.Message, state: FSMContext):
    await message.answer("So'z qo'shildi!")
    # db.add_word(message.text)
    await state.finish()



@dp.callback_query_handler(text_contains="black_list_delete_word")
async def black_list_delete_word(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=0)
    await query.message.answer("👇So'z o'chirish! Qora ro'yxatdan o'chirilishi kerak bo'lgan so'zni yuboring:")
    await BlackList.delete_word.set()


@dp.message_handler(state=BlackList.delete_word)
async def delete_word(message: types.Message, state: FSMContext):
    await message.answer("So'z o'chirildi!")
    # db.delete_word(message.text)
    await state.finish()


@dp.callback_query_handler(Text(equals="black_list_delete_all_words"))
async def black_list_delete_words(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=0)
    await query.message.answer("👇Barcha so'zlar o'chirildi!")
    # db.delete_words()
    await state.finish()