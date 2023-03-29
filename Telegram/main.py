import os
import threading
import time
from datetime import datetime, timedelta

import requests
import telebot
from telebot import types

from config import B_D, BASE, BOT_TOKEN, URL, RESULT_PATH
from to_result_db import *
from to_telegram_db import insert, select

bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message
insert = insert()
select = select()

#TODO: Удаление картинки после ответа. 
#TODO: Рандомные варианты
#TODO: QT форма

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    registration = types.KeyboardButton("Регистрация")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь в регистрации")
    markup.add(registration, information, bot_help)
    printy(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup=markup)


def interface(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    rating = types.KeyboardButton("Просмотреть работы")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь")
    markup.add(rating, information, bot_help)
    printy(message.chat.id, f"Возможности:", reply_markup=markup)


def registration_student(message):
    def one(message):
        printy(message.chat.id, f"Введите Ваше имя (оно будет показываться учителю)")
        insert.insert_id(message.chat.id)
        bot.register_next_step_handler(message, two)
    def two(message):
        insert.insert_name(message.chat.id, message.text)
        printy(message.chat.id, f"Введите Вашу фамилию (она будет показываться учителю)")
        bot.register_next_step_handler(message, three)
    def three(message):
        insert.insert_surname(message.chat.id, message.text)
        printy(message.chat.id, f"Введите ваш класс в формате: 10 А")
        bot.register_next_step_handler(message, four)
    def four(message):
        insert.insert_class(message.chat.id, message.text)
        printy(message.chat.id, f"Регистрация завершена")
        interface(message)
    one(message)


def view_questions(message):
    def take_number(message):
        if message.text == "Назад":
            return interface(message)
        create_tasks(message, message.text)
    try:
        os.chdir(B_D)
    except BaseException as e:
        pass
    list_return = ""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back = types.KeyboardButton("Назад")
    markup.add(back)

    printy(message.chat.id, 'Напишите номер варианта, который хотите решить. Или нажмите кнопку "Назад", чтобы вернуться назад', reply_markup=markup)
    printy(message.chat.id, "Список доступных вариантов:")

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
    printy(message.chat.id, list_return)
    bot.register_next_step_handler(message, take_number)


def create_tasks(message, number):
    answer = {}
    answers = {}
    tasks = []
    
    def delete_image(chat_id, delete):
        for message_id in delete:
            bot.delete_message(chat_id=chat_id, message_id=message_id)

    def view(message, task):
        os.chdir(BASE)
        #? Номер вопроса, имя файла карточки, время, правильный ответ, имя папки с карточками
        photo = {'photo': open(f"{task[4]}\{task[1]}", 'rb')}
        text = f"Номер вопроса: {task[0]}. Вам даётся {task[2]} минуты."
        sent = bot.send_photo(message.chat.id, photo=photo['photo'], caption=text)
        return sent.message_id

    def wait_answer(message, q, delete):
        answers[q] = "+"
        answer[q] = message.text
        delete_image(message.chat.id, delete)

    def view_tasks(message):
        delete = []
        stop = 0
        start = datetime.now()
        for task in tasks:
            if stop == 1:
                answer[int(task[0])] = None
                continue
            delete.append(view(message, task))
            delete.append(printy(message.chat.id, "Введите ответ (число или пара чисел, записанных через пробел)").message_id)
            while answers[int(task[0])] == "-":
                if datetime.now() > dt_time_stop:
                    printy(message.chat.id, f"Время кончилось.")
                    stop = 1
                    answer[int(task[0])] = None
                    break
                bot.register_next_step_handler(message, wait_answer, int(task[0]), delete)
                delete = []
                time.sleep(2)

        answer["name"] = name
        answer["surname"] = surname
        answer["class"] = learning_class
        answer["question"] = question
        answer["time_solve"] = str(round((datetime.now() - start).total_seconds() / 60, 2)) + "min"
        answer["user_id"] = message.chat.id
        answer["time_start"] = time_start

        os.chdir(B_D)
        check_question(message, number, answer)

    time_start = datetime.now().strftime('%d.%m.%Y %H:%M')
    printy(message.chat.id, f'''Вы начинаете решение варианта {number} \nНачало решения: {time_start}''')
    name = select.select_name(message.chat.id)
    surname = select.select_surname(message.chat.id)
    learning_class = select.select_class(message.chat.id)
    try:
        question = f"B{number}.txt"
        with open(question, "r") as file:
            time_ = 0
            file.readline()
            # print(file.readline().split("'")[0])
            for i in file.readlines():
                time_ += int(i.rstrip().split(";")[2])
                answers[int(i.rstrip().split(";")[0])] = "-"
            dt_time_stop = datetime.now() + timedelta(minutes=time_)
            file.close()
        with open(question, "r") as file:
            file.readline()
            for i in file.readlines():
                tasks.append(i.rstrip().split(";"))
    except BaseException as e:
        print(e)
        print("Ошибка показа варианта.")
        printy(message.chat.id, "Ошибка показа варианта.")
    else:
        t = threading.Thread(target=view_tasks, args=(message,))
        t.start()


def check_question(message, number, answer):
    printy(message.chat.id, f"Вариант {number} отправлен на проверку. Результаты вы можете посмотреть во вкладке: Просмотреть работы")
    print(answer)
    interface(message)
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

@bot.message_handler(content_types=["text"])
def check_text_message(message):
    if message.text == "Информация о боте":
        printy(message.chat.id, f"Бот создать специально для 44 Гимназии г.Пензы, для проверки знаний школьников")
        printy(message.chat.id, "Создатель бота: https://t.me/Mr_GoldSky")
    elif message.text == "Регистрация":
        registration_student(message)
    elif message.text == "Возможности":
        interface(message)
    elif message.text == "Помощь в регистрации":
        printy(message.chat.id, '''Помощь в регистрации: \n\
        1. Нажмите кнопку "Регистрация" \n\
        2. Введите ваше НАСТОЯЩЕЕ имя и фамилию \n\
        3. Введите класс в котором вы учитесь''')
    elif message.text == "Помощь":
        printy(message.chat.id, f'''Помощь: \n\
Нажав кнопку "Просмотреть работы" Можно будет посмотреть список заданных учителем вариантов. \n
Символом {chr(9989)} отмечены выполненные работы.
Символом {chr(9200)} отмечены работы, ожидающие выполнения. \n
После того, как вы сдадите работу, рядом будет стоять оценка''')
    elif message.text == "Просмотреть работы":
        view_questions(message)
    elif message.text == "":
        pass
    elif message.text == "":
        pass
    elif message.text == "":
        pass

bot.polling(none_stop=True)
