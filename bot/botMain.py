import os
import threading
import time
from datetime import datetime, timedelta

import requests
import telebot
from telebot import types

from bot.botConfig import EXAMS, TASKS, BOT_TOKEN, URL, RESULT_PATH
from bot.to_result_db import select_grade, select_percent, select_count, insert_result
from bot.to_telegram_db import insert, select

bot = telebot.TeleBot(BOT_TOKEN)

printy = bot.send_message
insert = insert()
select = select()

#TODO: Генератор вариантов
#TODO: Добавить action окно в журнал с иформацией о программе
#TODO: Сделать сортировку по классу/оценкам/дате
#TODO: Добавить комментарии
#TODO: Добавить возможность отключать время

# Старт обработчик
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    registration = types.KeyboardButton("Регистрация")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь в регистрации")
    markup.add(registration, information, bot_help)
    printy(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup=markup)

# Вывод интерфейся
def interface(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    rating = types.KeyboardButton("Просмотреть работы")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь")
    markup.add(rating, information, bot_help)
    printy(message.chat.id, f"Возможности:", reply_markup=markup)


# Регистрация пользователя
def registrationStudent(message):
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


# Вывод списка вариантов
def viewQuestions(message):
    def takeNumber(message):
        if message.text == "Назад":
            return interface(message)
        createTasks(message, message.text)

    listReturn = ""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back = types.KeyboardButton("Назад")
    markup.add(back)

    printy(message.chat.id, 'Напишите номер варианта, который хотите решить. Или нажмите кнопку "Назад", чтобы вернуться назад', reply_markup=markup)
    printy(message.chat.id, "Список доступных вариантов:")

    for i in os.listdir(EXAMS):
        try:
            grade = select_grade(message.chat.id, i)
            percent = select_percent(message.chat.id, i)
            count = select_count(message.chat.id, i)
            # Проверка, решал ли пользователь вариант. Вывод оценки и кол-ва решений
            if grade is None or count is None or count == 0:
                listReturn += f'№{i.replace(".txt", "").replace("B", "")} Работа не выполнена{chr(9200)} \n'
            else:
                listReturn += f'№{i.replace(".txt", "").replace("B", "")} {chr(9989)} {percent}% оценка {grade}. Кол-во решений: {count}\n'
        except BaseException as e: # Обработчик ошибки
            print(e)
            print("Вообще хз, что не так тут (viewQuestions)")
    printy(message.chat.id, listReturn)
    bot.register_next_step_handler(message, takeNumber)


# Создания варианта для отправки пользователю
def createTasks(message, number):
    answer = {}
    answers = {}
    tasks = []
    
    # Удаление отправленных сообщений
    def deleteImage(chat_id, delete):
        for message_id in delete:
            bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Отправка карточки с заданием
    def view(message, task):
        delete = []
        taskFolder = f'{TASKS}{task[4]}'
        mask = f'{task[4].replace("kge", "")}-{task[1].replace("(", " ").replace(")", " ").split()[1]}'

        # Поиск файлов, соответствующих маске
        matchingFiles = [f for f in os.listdir(taskFolder) if f.startswith(mask)]

        # Отправка карточки
        photo = {'photo': open(f"{taskFolder}\{task[1]}", 'rb')}
        text = f"Номер вопроса: {task[0]}. Вам даётся {task[2]} минуты."
        sent = bot.send_photo(message.chat.id, photo=photo['photo'], caption=text)

        # Отправка доп. файлов
        for filename in matchingFiles:
            filePath = f'{taskFolder}/{filename}'
            with open(filePath, 'rb') as file:
                doc = bot.send_document(message.chat.id, document=file)
                delete.append(doc.message_id)

        # Сохранение id сообщений для удаления 
        delete.append(sent.message_id)
        return delete
    
    def waitAnswer(message, q, delete):
        answers[q] = "+"
        answer[q] = message.text
        deleteImage(message.chat.id, delete)

    # Отправка карточек
    def viewTasks(message):
        if message.text == "Назад":
            return interface(message)
        
        delete = []
        stop = 0
        start = datetime.now()
        
        for task in tasks:
            if stop == 1:
                answer[int(task[0])] = None
                continue
            delete.extend(view(message, task))
            delete.append(printy(message.chat.id, "Введите ответ (число или пара чисел, записанных через пробел)").message_id)
            while answers[int(task[0])] == "-":
                
                #Проверка, что осталось время
                if datetime.now() > dt_time_stop:
                    printy(message.chat.id, f"Время кончилось.")
                    stop = 1
                    answer[int(task[0])] = None
                    break
                bot.register_next_step_handler(message, waitAnswer, int(task[0]), delete)
                delete = []
                time.sleep(2)

        # Сохранение результатов теста
        answer["name"] = name
        answer["surname"] = surname
        answer["class"] = learningClass
        answer["question"] = question
        answer["time_solve"] = str(round((datetime.now() - start).total_seconds() / 60, 2)) + "min"
        answer["user_id"] = message.chat.id
        answer["time_start"] = timeStart
        answer['answers'] = answers

        # Проверка ответов
        checkQuestion(message, number, answer)

    timeStart = datetime.now().strftime('%d.%m.%Y %H:%M')
    printy(message.chat.id, f'''Вы начинаете решение варианта {number} \nНачало решения: {timeStart}''')
    name = select.select_name(message.chat.id)
    surname = select.select_surname(message.chat.id)
    learningClass = select.select_class(message.chat.id)
    
    # Открытие txt файла с вариантом
    try:
        question = f"exams/B{number}.txt"
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
        print("Ошибка открытия варианта.")
        printy(message.chat.id, "Ошибка открытия варианта.")
    else:
        # Старт потока решения для пользователя
        t = threading.Thread(target=viewTasks, args=(message,))
        t.start()

# Проверка работы
def checkQuestion(message, number, answer):
    printy(message.chat.id, f"Вариант {number} отправлен на проверку. Результаты вы можете посмотреть во вкладке: Просмотреть работы")
    interface(message)
    countRight = 0 # Кол-во правильных решений
    with open(answer["question"], "r") as file:
        count = int(file.readline()[0])
        for i in file.readlines():
            if i.rstrip().split(";")[3] == answer[int(i.rstrip().split(";")[0])]: # Сверка ответов
                countRight += 1
                answer['answers'][int(i[0])] = chr(9989)
            else:
                answer['answers'][int(i[0])] = chr(10060)
        percent = round(countRight / count * 100, 2) # % выполнения работы
        
        # Выставление оценки
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
    print(answer)
    s = ''
    for i in range(len(answer['answers'])):
        s += f'Номер {i + 1} {answer["answers"][i + 1]} \n'
    printy(message.chat.id, f'''Вариант {number} Оценка {grade}
{s}''')

    # Сохранение результатов работы в БД
    name = answer["name"]
    surname = answer["surname"]
    learningClass = answer["class"]
    user_id = answer["user_id"]
    question = answer["question"][6:]
    timeStart = answer["time_start"]
    time_solve = answer["time_solve"]
    answers = str(answer["answers"]).replace(f'{chr(9989)}', '+').replace(f'{chr(10060)}', '-')

    insert_result(name, surname, learningClass, percent, grade, user_id, question, timeStart, time_solve, answers)

#     go_txt(answer)


# def go_txt(answer):
#     os.chdir(RESULT_PATH)
#     file_name = answer["surname"] + ".txt"
#     with open(file_name, "w") as file:
#         pass

# Обработчик кнопок
@bot.message_handler(content_types=["text"])
def check_text_message(message):
    if message.text == "Информация о боте":
        printy(message.chat.id, f"Бот создан специально для 44 Гимназии г.Пензы, для проверки знаний школьников")
        printy(message.chat.id, "Создатель бота: https://t.me/Mr_GoldSky")
    elif message.text == "Регистрация":
        registrationStudent(message)
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
        viewQuestions(message)
    elif message.text == "Назад":
        return interface(message)

def startBot():
    bot.polling(none_stop=True)

def stopBot():
    bot.stop_polling()
