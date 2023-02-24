import telebot
from telebot import types
from config import BOT_TOKEN, URL, BASE, B_D
from to_telegram_db import insert, select
from to_result_db import *
import os
from datetime import datetime, timedelta
import time
import requests


bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message
insert = insert()
select = select()


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
        view_question(message, message.text)
    try:
        os.chdir(B_D)
    except BaseException as e:
        pass
    list_return = ""
    printy(message.chat.id, 'Напишите номер варианта, который хотите решить. Или нажмите кнопку "Назад", чтобы вернуться назад')
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


def view_question(message, number):
    def view(message, task):
        os.chdir(BASE)
        #? Номер вопроса, имя файла карточки, время, правильный ответ, имя папки с карточками
        photo = {'photo': open(f"{task[4]}\{task[1]}", 'rb')}
        text = f"Номер вопроса: {task[0]}. Вам даётся {task[2]} минуты."
        requests.post(f'{URL}{BOT_TOKEN}/sendPhoto?chat_id={message.chat.id}&caption={text}', files=photo)
    
    time_start = datetime.now().strftime('%d.%m.%Y %H:%M')
    printy(message.chat.id, f'''Вы начинаете решение варианта {number} \nНачало решения: {time_start}''')
    name = select.select_name(message.chat.id)
    surname = select.select_surname(message.chat.id)
    learning_class = select.select_class(message.chat.id)
    try:
        question = f"B{number}.txt"
        insert_time_start(message.chat.id, time_start, question, name, surname, learning_class)
        with open(question, "r", encoding="utf8") as file:
            time = 0
            print(file.readline().split("'")[0])
            for i in file.readlines():
                time += int(i.rstrip().split(";")[2])
            time_start = datetime.now().strftime('%H:%M')
            dt_time_stop = datetime.now() + timedelta(minutes=time)
            file.close()
        with open(question, "r", encoding="utf8") as file:
            file.readline()
            for i in file.readlines():
                task = i.rstrip().split(";")
                if datetime.now() > dt_time_stop:
                    printy(message.chat.id, "Время кончилось")
                    break
                else:
                    view(message, task)

    except BaseException as e:
        print(e)
        print("Ошибка показа варианта.")
        printy(message.chat.id, "Ошибка показа варианта.")
    else:
        os.chdir(B_D)
        check_question(number, question)


def check_question(message, question):
    pass


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