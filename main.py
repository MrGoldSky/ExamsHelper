import telebot
from telebot import types
from to_db import insert, select

bot = telebot.TeleBot("5367101043:AAGIASVeQcYDvkNor-X2rE4YnVMWipH4N6g")
printy = bot.send_message
insert = insert()
select = select()

@bot.message_handler(commands=["start"])
def start(message):
    #TODO: Реализовать bot_help
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    registration = types.KeyboardButton("Регистрация")
    information = types.KeyboardButton("Информация о боте")
    bot_help = types.KeyboardButton("Помощь")
    markup.add(registration, information, bot_help)
    printy(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup=markup)

def interface(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    #TODO: Реализовать rating, bot_help
    if select.select_status(message.chat.id) == 0:
        rating = types.KeyboardButton("Просмотреть работы")
        information = types.KeyboardButton("Информация о боте")
        bot_help = types.KeyboardButton("Помощь")
        markup.add(rating, information, bot_help)
        printy(message.chat.id, f"Возможности:", reply_markup=markup)
    #TODO: Реализовать new_quest, rating, bot_help
    elif select.select_status(message.chat.id) == 1:
        new_quest = types.KeyboardButton("Задать новый вариант")
        rating = types.KeyboardButton("Просмотреть работы")
        information = types.KeyboardButton("Информация о боте")
        bot_help = types.KeyboardButton("Помощь")
        markup.add(new_quest, rating, bot_help, information)
        printy(message.chat.id, f"Возможности:!", reply_markup=markup)


def registration_student(message):
    insert.insert_status(message.chat.id, 0)
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

def registration_teacher(message):
    insert.insert_status(message.chat.id, 1)
    def one(message):
        printy(message.chat.id, f"Введите Ваше имя ")
        insert.insert_id(message.chat.id)
        bot.register_next_step_handler(message, two)
    def two(message):
        insert.insert_name(message.chat.id, message.text)
        printy(message.chat.id, f"Введите Вашу фамилию ")
        bot.register_next_step_handler(message, three)
    def three(message):
        insert.insert_last_name(message.chat.id, message.text)
        printy(message.chat.id, f"В каких классах вы преподаёте? Введите в формате: 10 А, 9 Б...")
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
        interface(message)
    elif message.text == "Регистрация":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        student = types.KeyboardButton("Ученик")
        teacher = types.KeyboardButton("Учитель")
        markup.add(student, teacher)
        printy(message.chat.id, f"Вы учитель или ученик?", reply_markup=markup)
    elif message.text == "Ученик":
        registration_student(message)
    elif message.text == "Учитель":
        printy(message.chat.id, "Введите пароль")
        bot.register_next_step_handler(message, check_text_message)
    elif message.text == "5525":
        registration_teacher(message)
    elif message.text == "Возможности":
        interface(message)

bot.polling(none_stop=True)