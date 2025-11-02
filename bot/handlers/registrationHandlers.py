from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.handlers.fsmStates import RegistrationStates
from bot.core.dependencyInjection import getContainer
from bot.handlers.commonHandlers import getRegisteredKeyboard
from utils.logger import botLogger


router = Router()
container = getContainer()


@router.message(F.text == "Регистрация")
async def cmdRegister(message: Message, state: FSMContext) -> None:
    userId = message.from_user.id

    if container.userRepository.userExists(userId):
        await message.answer("Вы уже зарегистрированы!")
        return

    container.userRepository.createUser(userId)
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer("Введите имя (буквы, пробел и дефис; 2–50 символов):")


@router.message(RegistrationStates.waiting_for_name)
async def processName(message: Message, state: FSMContext) -> None:
    if not container.validationService.validateName(message.text):
        await message.answer(
            "Некорректное имя. Разрешены буквы, пробел и дефис; длина от 2 до 50. Повторите ввод:"
        )
        return

    userId = message.from_user.id
    container.userRepository.updateName(userId, message.text.strip())
    await state.set_state(RegistrationStates.waiting_for_surname)
    await message.answer("Введите фамилию (буквы, пробел и дефис; 2–50 символов):")


@router.message(RegistrationStates.waiting_for_surname)
async def processSurname(message: Message, state: FSMContext) -> None:
    if not container.validationService.validateSurname(message.text):
        await message.answer(
            "Некорректная фамилия. Разрешены буквы, пробел и дефис; длина от 2 до 50. Повторите ввод:"
        )
        return

    userId = message.from_user.id
    container.userRepository.updateSurname(userId, message.text.strip())
    await state.set_state(RegistrationStates.waiting_for_class)
    await message.answer("Введите класс (например: 10 А, 11Б, 9):")


@router.message(RegistrationStates.waiting_for_class)
async def processClass(message: Message, state: FSMContext) -> None:
    if not container.validationService.validateClass(message.text):
        await message.answer("Некорректный формат класса. Примеры: 10 А, 11Б, 9.")
        return

    userId = message.from_user.id
    container.userRepository.updateClass(userId, message.text.strip())
    await state.clear()
    await message.answer("Регистрация завершена!", reply_markup=getRegisteredKeyboard())
    botLogger.info(f"User {userId} completed registration")
