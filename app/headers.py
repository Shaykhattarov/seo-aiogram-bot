import json, asyncio, os
import pandas as pd
from datetime import datetime, timedelta
from app import bot, dp, config
from aiogram.types import Message, CallbackQuery, MediaGroup, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.keyboards import start, section, test



def read_files_map():
    """ Чтение карты файлов """
    with open(config.FILE_MAP, 'r', encoding='utf-8') as file:
        json_map = json.load(file)
    return json_map


def read_file(filename):
    """ Чтение файла """
    with open(os.path.join(config.FILEPATH, filename), 'rb') as file:
        return file.read()


def search_excel_file():
    files = os.listdir(config.FILE_TESTS_PATH)
    result = []
    
    for file in files:
        filesplitted = file.split('.')
        if filesplitted[1] == 'xlsx':
            result.append(file) 
    return result[0] 


def parse_excel_file():
    filename = search_excel_file()
    if filename is None or filename == '':
        return {
            'status': 'error',
            'message': 'Не найдены тесты'
        }
    filepath = os.path.join(config.FILE_TESTS_PATH, filename)
    data = dict()
    data['modelling'] = [{'question': 'empty', 'answers': [], 'true_answer': ''}]
    data['interfaces'] = [{'question': 'empty', 'answers': [], 'true_answer': ''}]
    xl = pd.read_excel(filepath)
    df = pd.DataFrame(xl, columns=['Номер', 'Предмет', 'Тема', 'Вопрос', 'Ответ верный', 'Ответ_1', 'Ответ_2', 'Ответ_3'])
    for count in range(len(df)):
        if df['Предмет'][count] == 'Моделирование':
            data['modelling'].append({'question': df['Вопрос'][count], 'answers': [df['Ответ_1'][count], df['Ответ_2'][count], df['Ответ_3'][count], df['Ответ верный'][count]], "true_answer": df['Ответ верный'][count]})

        if df['Предмет'][count] == 'ЧМИ':
            data['interfaces'].append({'question': df['Вопрос'][count], 'answers': [df['Ответ_1'][count], df['Ответ_2'][count], df['Ответ_3'][count], df['Ответ верный'][count]], "true_answer": df['Ответ верный'][count]})
    
    return {
        'status': 'good',
        'message': data
    }



class Test(StatesGroup):
    start_time = State()
    end_time = State()
    excel = State()
    true_count = State()
    subject = State()
    mistakes = State()



@dp.message_handler(commands=['start', 'subjects'])
async def start_message(message: Message):
    """ Приветственное сообщение """
    match message.text:
        case '/start': 
            return await message.answer(text="Привет, я твой личный помошник в обучении. Выбери, какой предмет тебя "
                                "интересует, а я пришлю тебе необходимый материал для изучения", reply_markup=start.markup)
        case '/subjects':
            return await message.answer(text="Выбери, какой предмет тебя интересует, а я пришлю тебе необходимый материал для изучения", reply_markup=start.markup) 



@dp.callback_query_handler(lambda c: c.data.startswith('subject-'))
async def choosen_subject_message(call: CallbackQuery):
    """ Сообщение выбора необходимого материала """
    subject = call.data.replace('subject-', '')
    return await bot.send_message(chat_id=call.from_user.id, text='Выбери раздел, который тебя интересует', reply_markup=section.generate_section_markup(subject=subject))



@dp.callback_query_handler(lambda c: c.data.startswith('lection-'))
async def choosen_materials_message(call: CallbackQuery):
    """ Вывод выбранных материалов """
    subject = call.data.replace('lection-', '')
    
    loop = asyncio.get_event_loop() # Не ломаем ассинхронность
    json_map = await loop.run_in_executor(None, read_files_map) # Читаем файл карты материалов в executor`e
    
    if subject == 'interfaces':
        text = "Лекционный материал по предмету Человеко-машинные интерфейсы:\n#ЛекцииЧМИ"
    else:
        text = "Лекционный материал по предмету Моделирование:\n#ЛекцииМоделирование"
    
    await bot.send_message(chat_id=call.from_user.id, text=text)
    media = MediaGroup()
    
    for lection in json_map['subject'][subject]['lection']:
        caption = lection['text']
        filenames = lection['filenames']
        
        for filename in filenames:
            media.attach_document(caption=caption, document=InputFile(os.path.join(config.FILEPATH, filename)))
    
    return await bot.send_media_group(chat_id=call.from_user.id, media=media)



@dp.callback_query_handler(lambda c: c.data.startswith('practice-'))
async def choosen_practice_message(call: CallbackQuery):
    """ Вывод выбранных практических заданий """
    subject = call.data.replace('practice-', '')
    loop = asyncio.get_event_loop() # Не ломаем ассинхронность
    json_map = await loop.run_in_executor(None, read_files_map) # Читаем файл карты материалов в executor`e

    if subject == 'interfaces':
        text = 'Лабораторные работы по предмету Человеко-машинные интерфейсы:\n#ЛабораторныеЧМИ'
    else:
        text = "Лабораторные работы по предмету Моделирование:\n#ЛабораторныеМоделирование"
    await bot.send_message(chat_id=call.from_user.id, text=text)
    media = MediaGroup()
    
    for lection in json_map['subject'][subject]['practice']:
        caption = lection['text']
        filenames = lection['filenames']
        
        for filename in filenames:
            try:
                inputfile = InputFile(os.path.join(config.FILEPATH, filename))    
            except Exception as err:
                print(f'Ошибка при открытии файла: {err}')
            else:
                media.attach_document(caption=caption, document=inputfile)
    
    return await bot.send_media_group(chat_id=call.from_user.id, media=media)



@dp.callback_query_handler(lambda c: c.data.startswith('test-'), state='*')
async def choosen_test_message(call: CallbackQuery, state: FSMContext):
    """ Вывод выбранных тестов """
    subject = call.data.replace('test-', '')
    loop = asyncio.get_event_loop() # Не ломаем ассинхронность
    excel = await loop.run_in_executor(None, parse_excel_file) # Читаем файл excel в executor`e
    
    if excel['status'] == 'error':
        return await bot.send_message(chat_id=call.from_user.id, text=excel['message'])
    
    excel_data = excel['message']

    await state.update_data(
        subject=subject,
        excel=excel_data[subject],
        true_count=0,
        mistakes=[],
        start_time=datetime.now(),
        question_number=0,
        end_time=datetime.now() + timedelta(minutes=config.TEST_TIME_MINUTES)
    )

    if subject == 'modelling':
        text = f"Вы хотите пройти тест по предмету Моделирование. Он будет длиться {config.TEST_TIME_MINUTES} минут. Вы готовы?"
        markup = test.generate_start_test_markup()
    else:
        text = f"Вы хотите пройти тест по предмету Человек-машинные интерфейсы. Он будет длиться {config.TEST_TIME_MINUTES} минут. Вы готовы?"
        markup = test.generate_start_test_markup()
        
    return await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('answer-'), state='*')
async def generate_test_question(call: CallbackQuery, state: FSMContext):
    """ Генерация и проверка вопросов и ответов теста """
    state_data = await state.get_data() # Получаем данные из state
    
    if datetime.now() >= state_data['end_time']:
        # Проверка на время, если время закончилось то сразу переход к просмотру результатов
        markup = test.generate_view_result_markup()
        return await bot.send_message(chat_id=call.from_user.id, text="Ваше время закончилось!", reply_markup=markup)
    
    question_number: int = state_data['question_number']
    call_answer_number: int = int(call.data.split('-')[2])
    call_question_number: int = int(call.data.split('-')[1])
    excel: dict = state_data['excel']
    true_count: int = state_data['true_count']
    mistakes: list = state_data['mistakes']
    
    if question_number == 0 and call_question_number != 0:
        # Если пользователь уже начал тест и хочет еще раз нажать на клавишу начать тест
        return await bot.send_message(chat_id=call.from_user.id, text="Вы уже начали тест, доведите его до конца!")
    
    if question_number == 0 and call_question_number == 0:
        # Самое первое сообщение перед тестов "Начать тест"
        question_number = 1
        await state.update_data(question_number=question_number)

        markup = test.generate_answer_choose_markup(answers=excel[question_number]['answers'], number=(question_number))
        text = f'Вопрос №{question_number}\n{excel[question_number]["question"]}'
    
        return await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=markup)
    
    if call_question_number != question_number:
        return await bot.send_message(chat_id=call.from_user.id, text="Вы уже отвечали на этот вопрос!")
    
    if (question_number + 1) >= len(excel):
        # Проверка на послдений вопрос, если вопрос был последний, то сообщаем об этом пользователю
        markup = test.generate_view_result_markup()
        time = str(datetime.now() - state_data['start_time']).split('.')[0]
        await state.update_data(
            all_time=datetime.now() - state_data['start_time']
        )
        return await bot.send_message(chat_id=call.from_user.id, text=f"Вы закончили тест за {time}" ,reply_markup=markup)
    
    if excel[question_number]['answers'][call_answer_number] == excel[question_number]['true_answer']:
        # Если ответ пользователя правильный
        true_count += 1
        question_number += 1

        await state.update_data(true_count=true_count, question_number=question_number)
    else:
        # Если ответ не верный
       
        mistakes.append({'number': question_number, 'answer': excel[question_number]['answers'][call_answer_number], 'true_answer': excel[question_number]['true_answer']})
        question_number += 1
        await state.update_data(question_number=question_number, mistakes=mistakes)

    
    question = excel[question_number]['question']
    text = f"Вопрос №{question_number}\n{question}"
    markup = test.generate_answer_choose_markup(answers=excel[question_number]['answers'], number=(question_number))
    
    return await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=markup)



@dp.callback_query_handler(lambda c: c.data.startswith('result-'), state='*')
async def view_test_result(call: CallbackQuery, state: FSMContext):
    """ Отображение ответов теста """
    state_data = await state.get_data()
    
    if state_data is None:
        text = "Вы еще не проходили тест. Выберите предмет и пройдите его сейчас!"
        return await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=start.markup)
    
    mistakes_text = '*Неправильные ответы:*\n'
    for mistake in state_data['mistakes']:
        mistakes_text += f"*Вопрос №{mistake['number']}* - *Ответ:* {mistake['answer']} - *Верный ответ:* {mistake['true_answer']}\n"
    text = f"Ты успешно прошел тест. Вот твои результаты:\n*Время*: {str(state_data['all_time']).split('.')[0]}\n*Количество правильных ответов*: {state_data['true_count']}"
    grade_text = f"Твой балл по результатам теста: {'{:.2f}'.format(round(len(mistake) / len(state_data['excel']), 2))}"
    await bot.send_message(chat_id=call.from_user.id, text=text, parse_mode="Markdown")
    await bot.send_message(chat_id=call.from_user.id, text=mistakes_text, parse_mode="Markdown")
    await bot.send_message(chat_id=call.from_user.id, text=grade_text, parse_mode="Markdown")