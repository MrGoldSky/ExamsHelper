import telebot
from telebot import types
from config import BOT_TOKEN, RESULT_BASE_PATH
from to_db import insert, select
import os
import sqlite3

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
    #TODO: Реализовать rating
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
        insert.insert_last_name(message.chat.id, message.text)
        printy(message.chat.id, f"Введите ваш класс в формате: 10 А")
        bot.register_next_step_handler(message, four)
    def four(message):
        insert.insert_class(message.chat.id, message.text)
        printy(message.chat.id, f"Регистрация завершена")
        interface(message)
    one(message)

def view_questions(message):
    def take_number(message):
        printy(message.chat.id, f"Вариант {message.text}")
        view_question(message, message.text)
    
    os.chdir("Project_school/B_D")
    list_return = ""
    printy(message.chat.id, "Напишите номер варианта, которых хотите решить")
    printy(message.chat.id, "Список доступных вариантов:")
    con, cur = connect_to_db()


    for i in os.listdir():
        try:
            grade = cur.execute(f"""SELECT grade from base WHERE user_id = {message.chat.id}
                    """).fetchone()[0]
            con.close()
        except BaseException:
            list_return += f'{i.replace(".txt", "").replace("B", "")} Работа не выполнена{chr(9200)} \n'
        else:
            list_return += f'{i.replace(".txt", "").replace("B", "")} {chr(9989)} {grade} \n'
    printy(message.chat.id, list_return)
    bot.register_next_step_handler(message, take_number)

def connect_to_db():
    try:
        con = sqlite3.connect(RESULT_BASE_PATH)
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        print(e)
        print("Ошибка подключения к БД")

def view_question(message, number):
    print(os.getcwd())
    with open(f"B{number}.txt", "r") as file:
        print(file.readline().split("'")[0])
        for i in file.readlines():
            print(i.rstrip())


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
        2. Введите ваше НАСТОЯЩЕЕ имя и фамилию. \n\
        3. Введите класс в котором вы учитесь/преподаёте.''')
    #TODO: Доделать помощь 
    elif message.text == "Помощь":
        printy(message.chat.id, f'''Помощь: \n\
Нажав кнопку "Просмотреть работы" Можно будет посмотреть список заданных учителем вариантов. \n
Символом {chr(9989)} отмечены выполненные работы.
Символом {chr(9200)} отмечены работы, ожидающие выполнения. \n
После того, как вы сдадите работу, рядом будет написан % решения и оценка''')
    elif message.text == "Просмотреть работы":
        view_questions(message)
    elif message.text == "":
        pass
    elif message.text == "":
        pass
    elif message.text == "":
        pass

bot.polling(none_stop=True)