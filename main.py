import telebot
from telebot import types
from to_db import insert, select

bot = telebot.TeleBot("5367101043:AAGIASVeQcYDvkNor-X2rE4YnVMWipH4N6g")
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
    bot_help = types.KeyboardButton("Помощь ученику")
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
        2. Выберете, кто вы. Учитель или Ученик. \n\
        3. Введите ваше НАСТОЯЩЕЕ имя и фамилию. \n\
        4. Введите класс в котором вы учитесь/преподаёте.''')
    #TODO: Доделать помощь 
    elif message.text == "Помощь ученику":
        printy(message.chat.id, f'''Помощь ученику: \n\
Нажав кнопку "Просмотреть работы" Можно будет посмотреть список заданных учителями работ. \n
Символом {chr(9989)} отмечены выполненные работы.
Символом {chr(9200)} отмечены работы, ожидающие выполнения. Рядом с ними написанно крайнее время сдачи. \n
После того, как все ученики сдадут работы или закончится время, рядом с работой будет написан % решения и оценка.''')
    elif message.text == "":
        pass
    elif message.text == "":
        pass
    elif message.text == "":
        pass
    elif message.text == "":
        pass

bot.polling(none_stop=True)