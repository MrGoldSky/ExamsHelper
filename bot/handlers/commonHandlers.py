from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from bot.core.dependencyInjection import getContainer
from utils.logger import botLogger


router = Router()
container = getContainer()


def getMainKeyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Регистрация")],
            [KeyboardButton(text="Информация о проекте"), KeyboardButton(text="Помощь по регистрации")]
        ],
        resize_keyboard=True
    )
    return keyboard


def getRegisteredKeyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Решать экзамены")],
            [KeyboardButton(text="Информация о проекте"), KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


@router.message(Command("start"))
async def cmdStart(message: Message) -> None:
    userId = message.from_user.id

    if container.userRepository.userExists(userId):
        await message.answer(
            f"Привет, {message.from_user.first_name}!",
            reply_markup=getRegisteredKeyboard()
        )
    else:
        await message.answer(
            f"Привет, {message.from_user.first_name}!",
            reply_markup=getMainKeyboard()
        )


@router.message(F.text == "Информация о проекте")
async def cmdInfo(message: Message) -> None:
    text = (
        "Бот помогает тренироваться к экзаменам и решать варианты. Основан на aiogram, SQLite3, PyQt5.\n\n"
        "Контакты разработчика: https://t.me/Mr_GoldSky\n"
        "Материалы и задания: сайт К. Полякова — https://kpolyakov.spb.ru/"
    )
    await message.answer(text)


@router.message(F.text == "Помощь по регистрации")
async def cmdRegistrationHelp(message: Message) -> None:
    text = (
        "Помощь по регистрации:\n\n"
        "1. Нажмите кнопку \"Регистрация\"\n"
        "2. Введите имя, фамилию и класс в требуемом формате\n"
        "3. Проверьте данные и подтвердите регистрацию"
    )
    await message.answer(text)


@router.message(F.text == "Помощь")
async def cmdHelp(message: Message) -> None:
    text = (
        "Помощь:\n\n"
        "Выберите \"Решать экзамены\" чтобы начать тренировку — бот покажет список доступных вариантов.\n"
        f"Зелёная галочка {chr(9989)} — выполнено верно.\n"
        f"Песочные часы {chr(9200)} — вариант ещё не решался.\n\n"
        "Если что-то пошло не так или есть вопросы, напишите разработчику."
    )
    await message.answer(text)
