from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup



def generate_start_test_markup():
    buttons = [InlineKeyboardButton('Начать тест', callback_data=f'answer-0-0')]
    return InlineKeyboardMarkup(resize_keyboard=True).row(*buttons)


def generate_answer_choose_markup(answers: list, number: int):
    markup = InlineKeyboardMarkup()
    for num, answer in enumerate(answers):
        button = InlineKeyboardButton(answer, callback_data=f'answer-{number}-{num}')
        markup.add(button)
    return markup
    

def generate_view_result_markup():
    buttons = [InlineKeyboardButton('Посмотреть результат', callback_data=f'result-')]
    return InlineKeyboardMarkup().add(*buttons)


