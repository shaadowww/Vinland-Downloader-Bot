from aiogram.types import  InlineKeyboardMarkup , InlineKeyboardButton

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="start", callback_data="start")]
    ])

work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="run", callback_data="Run")]
    ])