from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

buttons = [
        InlineKeyboardButton(text="Человеко-Машинные интерфейсы", callback_data='subject-interfaces'),
        InlineKeyboardButton(text="Моделирование", callback_data='subject-modelling'),
    ]

markup = InlineKeyboardMarkup(row_width=1).add(*buttons)