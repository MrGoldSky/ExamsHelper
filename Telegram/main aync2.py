import os
import threading
import time
from datetime import datetime, timedelta

import requests

from config import B_D, BASE, BOT_TOKEN, URL, RESULT_PATH
from to_result_db import *
from to_telegram_db import insert, select

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, CallbackQuery, InputFile
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio

from functools import partial


bot = aiogram.Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

printy = bot.send_message
insert = insert()
select = select()

#TODO: Рандомные варианты
#TODO: QT форма

class Registration(StatesGroup):
    name = State()      # состояние для имени пользователя
    surname = State()   # состояние для фамилии пользователя
    class_num = State() # состояние для класса пользователя

class TakeNumber(StatesGroup):
    number = State()

class WaitAnswer(StatesGroup):
    waiting_for_answer = State()

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    registration = types.KeyboardButton("Регистрация")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь в регистрации")
    markup.add(registration, information, bot_help)
    await printy(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup=markup)


@dp.message_handler(content_types=types.ContentTypes.TEXT, text="Регистрация")
async def registration_student(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    await printy(message.chat.id, f"Введите Ваше имя (оно будет показываться учителю)", reply_markup=markup)

    # переключение на первое состояние - ввод имени пользователя
    await Registration.name.set()

# обработчик для первого состояния - ввод имени пользователя
@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    # сохранение введенного имени в хранилище состояний
    async with state.proxy() as data:
        data['name'] = message.text

    markup = types.ReplyKeyboardRemove()
    await printy(message.chat.id, f"Введите Вашу фамилию (она будет показываться учителю)", reply_markup=markup)

    # переключение на второе состояние - ввод фамилии пользователя
    await Registration.surname.set()

# обработчик для второго состояния - ввод фамилии пользователя
@dp.message_handler(state=Registration.surname)
async def process_surname(message: types.Message, state: FSMContext):
    # сохранение введенной фамилии в хранилище состояний
    async with state.proxy() as data:
        data['surname'] = message.text

    markup = types.ReplyKeyboardRemove()
    await printy(message.chat.id, f"Введите ваш класс в формате: 10 А", reply_markup=markup)

    # переключение на третье состояние - ввод класса пользователя
    await Registration.class_num.set()

# обработчик для третьего состояния - ввод класса пользователя
@dp.message_handler(state=Registration.class_num)
async def process_class_num(message: types.Message, state: FSMContext):
    # сохранение введенного класса в хранилище состояний
    async with state.proxy() as data:
        data['class_num'] = message.text

    # получение сохраненных данных из хранилища состояний
    data = await state.get_data()
    
    # Сохранение данных в БД 
    insert.insert_id(message.chat.id)
    insert.insert_name(message.chat.id, data['name'])
    insert.insert_surname(message.chat.id, data['surname'])
    insert.insert_class(message.chat.id, data['class_num'])
    
    # вывод результата регистрации и переключение на начальное состояние
    await printy(message.chat.id, f"Регистрация завершена")
    await interface(message)

    await state.finish()

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="Возможности")
async def interface(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    rating = types.KeyboardButton("Просмотреть работы")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь")
    markup.add(rating, information, bot_help)
    await printy(message.chat.id, f"Возможности:", reply_markup=markup)

@dp.message_handler(state=TakeNumber.number)
async def take_number(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await interface(message)
        await state.finish()
        return
    await create_tasks(message, message.text, state)
    await state.finish()

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="Просмотреть работы")
async def view_questions(message: types.Message, state: FSMContext):
    try:
        os.chdir(B_D)
    except BaseException as e:
        pass

    list_return = ""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back = types.KeyboardButton("Назад")
    markup.add(back)

    await message.answer('Напишите номер варианта, который хотите решить. Или нажмите кнопку "Назад", чтобы вернуться назад', reply_markup=markup)
    await message.answer("Список доступных вариантов:")

    for i in os.listdir():
        try:
            grade = select_grade(message.chat.id, i)
            percent = select_percent(message.chat.id, i)
            count = select_count(message.chat.id, i)
            if grade is None or count is None or count == 0:
                list_return += f'№{i.replace(".txt", "").replace("B", "")} Работа не выполнена{chr(9200)} \n'
            else:
                list_return += f'№{i.replace(".txt", "").replace("B", "")} {chr(9989)} {percent}% оценка {grade}. Кол-во решений: {count}\n'
        except BaseException as e:
            print(e)
            print("Вообще хз, что не так тут (view_questions)")

    await message.answer(list_return, reply_markup=markup)
    await TakeNumber.number.set()


async def create_tasks(message, number, state):
    async with state.proxy() as data:
        data['delete'] = []
        data['q'] = 1
    
    name = select.select_name(message.chat.id)
    surname = select.select_surname(message.chat.id)
    learning_class = select.select_class(message.chat.id)

    @dp.message_handler(state=WaitAnswer.waiting_for_answer)
    async def wait_answer(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            q = int(data['q'])
            delete = data['delete']
            for id_ in delete:
                await bot.delete_message(chat_id=message.chat.id, message_id=id_)
            data["delete"] = []
            await state.finish()

    async def view_tasks(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            stop = 0
            start = datetime.now()
            for task in data['tasks']:
                print(task)
                data['q'] = int(task[0])
                if stop == 1:
                    data['answers'][int(task[0])] = None
                    continue
                photo = InputFile(os.path.join(BASE, task[4], task[1]))
                text = f"Номер вопроса: {task[0]}. Вам даётся {task[2]} минуты."
                sent = await bot.send_photo(message.chat.id, photo=photo, caption=text)
                data['delete'].append(sent.message_id)
                data['delete'].append((await printy(message.chat.id, "Введите ответ (число или пара чисел, записанных через пробел)")).message_id)

                while data['answers'][int(task[0])] == "-":
                    if datetime.now() > dt_time_stop:
                        await message.reply("Время кончилось.")
                        stop = 1
                        data['answers'][int(task[0])] = None
                        break
                    await WaitAnswer.waiting_for_answer.set()
                    await asyncio.sleep(2)

            data["name"] = name
            data["surname"] = surname
            data["class"] = learning_class
            data["time_solve"] = str(round((datetime.now() - start).total_seconds() / 60, 2)) + "min"
            data["user_id"] = message.chat.id
            data["time_start"] = time_start

            os.chdir(B_D)
            await check_question(message, number, data['answers'])
    
    async def start_solve(message: types.Message, state: FSMContext):
        global question, time_start, dt_time_stop
        await printy(message.chat.id, f'Вы начинаете решение варианта {number}')
        time_start = datetime.now().strftime('%d.%m.%Y %H:%M')
        async with state.proxy() as data:
            data['question'] = f'B{number}.txt'
            data['answers'] = {}
            data['tasks'] = []
            data['time_start'] = time_start
            with open(data['question'], "r") as file:
                time_ = 0
                file.readline()
                for i in file.readlines():
                    time_ += int(i.rstrip().split(";")[2])
                    data['answers'][int(i.rstrip().split(";")[0])] = "-"
                dt_time_stop = datetime.now() + timedelta(minutes=time_)
                file.close()
            with open(data['question'], "r") as file:
                file.readline()
                for i in file.readlines():
                    data['tasks'].append(i.rstrip().split(";"))
        await view_tasks(message, state)
    
    async def start_solve_wrapper(message: types.Message, state: FSMContext):
        await start_solve(message, state=state)
    await start_solve_wrapper(message, state=state)

async def check_question(message: types.Message, number: int, answer: dict):
    await bot.send_message(message.chat.id, f"Вариант {number} отправлен на проверку. Результаты вы можете посмотреть во вкладке: Просмотреть работы")
    print(answer)
    await interface(message)
    count_right = 0
    with open(answer["question"], "r") as file:
        count = int(file.readline()[0])
        for i in file.readlines():
            if i.rstrip().split(";")[3] == answer[int(i.rstrip().split(";")[0])]:
                count_right += 1
        percent = round(count_right / count * 100, 2)
        if percent >= 85:
            grade = 5
        elif percent  >= 70:
            grade = 4
        elif percent >= 50:
            grade = 3
        elif percent >= 40:
            grade = 2
        else:
            grade = 1
    await bot.send_message(message.chat.id, f"Процент правильных ответов: {percent}%\nОценка: {grade}")

    name = answer["name"]
    surname = answer["surname"]
    learning_class = answer["class"]
    user_id = answer["user_id"]
    question = answer["question"]
    time_start = answer["time_start"]
    time_solve = answer["time_solve"]

    insert_result(name, surname, learning_class, percent, grade, user_id, question, time_start, time_solve)

#     go_txt(answer)


# def go_txt(answer):
#     os.chdir(RESULT_PATH)
#     file_name = answer["surname"] + ".txt"
#     with open(file_name, "w") as file:
#         pass

@dp.message_handler(content_types=types.ContentType.TEXT)
async def check_text_message(message: types.Message):
    if message.text == "Информация о боте":
        await bot.send_message(message.chat.id, "Бот создан специально для 44 Гимназии г.Пензы, для проверки знаний школьников")
        await bot.send_message(message.chat.id, "Создатель бота: https://t.me/Mr_GoldSky")
    # elif message.text == "Регистрация":
    #     await registration_student(message)
    # elif message.text == "Возможности":
    #     await interface(message)
    elif message.text == "Помощь в регистрации":
        await bot.send_message(message.chat.id, '''Помощь в регистрации: \n\
        1. Нажмите кнопку "Регистрация" \n\
        2. Введите ваше НАСТОЯЩЕЕ имя и фамилию \n\
        3. Введите класс в котором вы учитесь''')
    elif message.text == "Помощь":
        await bot.send_message(message.chat.id, f'''Помощь: \n\
Нажав кнопку "Просмотреть работы" Можно будет посмотреть список заданных учителем вариантов. \n
Символом {chr(9989)} отмечены выполненные работы.
Символом {chr(9200)} отмечены работы, ожидающие выполнения. \n
После того, как вы сдадите работу, рядом будет стоять оценка''')
    # elif message.text == "Просмотреть работы":
    #     await view_questions(message, dp)
    elif message.text == "":
        pass
    elif message.text == "":
        pass
    elif message.text == "":
        pass


if __name__ == "__main__":
    aiogram.executor.start_polling(dp, skip_updates=True)

