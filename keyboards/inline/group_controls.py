from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MainMenuControl = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        # [InlineKeyboardButton(text="Guruhlar ro'yxati", callback_data="group_list")],
        [InlineKeyboardButton(text="Guruhga avto reklama tashlash", callback_data="auto_advertising")],
        [InlineKeyboardButton(text="Guruhga reklama tashlash", callback_data="advertising")],
        [InlineKeyboardButton(text="Guruhga pin reklama tashlash", callback_data="pin_advertising")],
    ]
)