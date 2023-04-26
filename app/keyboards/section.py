from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def generate_section_markup(subject: str):
    """ Генерация клавиатуры для выбора материала работ """
    buttons = [
        InlineKeyboardButton('Лекции', callback_data=f'lection-{subject}'),
        InlineKeyboardButton('Лабораторные работы', callback_data=f'practice-{subject}'),
        InlineKeyboardButton('Пройти тест', callback_data=f'test-{subject}'),
        InlineKeyboardButton("Вернуться к выбору предмета", callback_data='choose-subject')
    ]

    markup = InlineKeyboardMarkup().add(*buttons)

    return markup