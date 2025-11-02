from datetime import datetime
from typing import Dict, Any

from aiogram import Router, F
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext

from bot.handlers.fsmStates import ExamStates
from bot.core.dependencyInjection import getContainer
from bot.handlers.commonHandlers import getRegisteredKeyboard
from utils.logger import botLogger


router = Router()
container = getContainer()

SKIP_CALLBACK_PREFIX = "skip_task"
FINISH_CALLBACK = "finish_exam"
SKIP_ANSWER = "__SKIP__"
FINISH_ANSWER = "__FINISH__"


def getBackKeyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
    )


@router.message(F.text == "Решать экзамены")
async def cmdViewExams(message: Message, state: FSMContext) -> None:
    userId = message.from_user.id

    if not container.userRepository.userExists(userId):
        await message.answer("Сначала пройдите регистрацию!")
        return

    availableExams = container.examService.getAvailableExams()
    if not availableExams:
        await message.answer("Нет доступных экзаменов.")
        return

    examList = "Список доступных экзаменов:\n\n"
    for examName in availableExams:
        grade = container.resultRepository.getMaxGrade(userId, f"{examName}.txt")
        percent = container.resultRepository.getMaxPercent(userId, f"{examName}.txt")
        count = container.resultRepository.getCount(userId, f"{examName}.txt")

        if grade is None or count == 0:
            examList += f"- {examName} ⌛ ещё не решался\n"
        else:
            examList += f"- {examName} {chr(9989)} {percent}% оценка {grade}. Попыток: {count}\n"

    await message.answer(
        'Отправьте точное название экзамена из списка ниже. Для возврата нажмите «Назад».',
        reply_markup=getBackKeyboard()
    )
    await message.answer(examList)
    await state.set_state(ExamStates.waiting_for_exam_selection)


@router.message(ExamStates.waiting_for_exam_selection)
async def processExamSelection(message: Message, state: FSMContext) -> None:
    if message.text == "Назад":
        await state.clear()
        await message.answer("Вы в главном меню", reply_markup=getRegisteredKeyboard())
        return

    availableExams = container.examService.getAvailableExams()
    examName = container.validationService.validateExamName(message.text, availableExams)

    if not examName:
        await message.answer("Такого экзамена нет. Введите название из списка выше:")
        return

    userId = message.from_user.id
    examData = container.examService.loadExam(examName)

    if not examData:
        await message.answer("Не удалось загрузить выбранный экзамен.")
        return

    await startExam(message, state, userId, examData, examName)


async def startExam(message: Message, state: FSMContext, userId: int, examData: Dict[str, Any], examName: str) -> None:
    timeStart = datetime.now().strftime('%d.%m.%Y %H:%M')

    sessionData = {
        'examName': examName,
        'examData': examData,
        'userAnswers': {},
        'timeStart': timeStart,
        'startDateTime': datetime.now(),
        'messageIds': []
    }

    container.answerWaiterService.createExamSession(userId, sessionData)

    await message.answer(
        f"Вы начали решать экзамен {examName}\nНачало: {timeStart}"
    )

    await state.set_state(ExamStates.solving_exam)
    await processNextTask(message, userId)


async def processNextTask(message: Message, userId: int) -> None:
    session = container.answerWaiterService.getExamSession(userId)
    if not session:
        return

    examData = session['examData']
    tasks = examData['tasks']
    currentTaskNum = len(session['userAnswers']) + 1

    if currentTaskNum > len(tasks):
        await finishExam(message, userId, session)
        return

    task = tasks[currentTaskNum - 1]
    taskImagePath = container.examService.getTaskImagePath(task['folder'], task['file'])

    if not taskImagePath or not taskImagePath.exists():
        botLogger.error(f"Task image not found: {taskImagePath}")
        await message.answer(f"Не удалось показать задание {task['number']}")
        await finishExam(message, userId, session)
        return

    try:
        photo = FSInputFile(taskImagePath)
        sentPhoto = await message.answer_photo(
            photo,
            caption=f"Задание №{task['number']}. Время на ответ: {task['time_limit']} мин."
        )
        session['messageIds'].append(sentPhoto.message_id)

        additionalFiles = container.examService.getTaskAdditionalFiles(task['folder'], task['file'])
        for filePath in additionalFiles:
            doc = FSInputFile(filePath)
            sentDoc = await message.answer_document(doc)
            session['messageIds'].append(sentDoc.message_id)

        prompt_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Пропустить задание",
                        callback_data=f"{SKIP_CALLBACK_PREFIX}:{task['number']}"
                    ),
                    InlineKeyboardButton(
                        text="Завершить досрочно",
                        callback_data=FINISH_CALLBACK
                    ),
                ]
            ]
        )
        prompt_message = await message.answer(
            "Введите ответ (только числа, допускаются точки и дефисы; например: 12-34 или 3.14):",
            reply_markup=prompt_keyboard
        )
        session['messageIds'].append(prompt_message.message_id)

        container.answerWaiterService.createFutureForUser(userId)
        answer = await container.answerWaiterService.waitForAnswer(
            userId,
            task['time_limit'],
            examData['time_enabled'],
            session['startDateTime']
        )

        if answer == FINISH_ANSWER:
            await deleteTaskMessages(message, session)
            await finishExam(message, userId, session)
            return
        if answer == SKIP_ANSWER:
            session['userAnswers'][task['number']] = None
            await deleteTaskMessages(message, session)
            await message.answer("Задание пропущено.")
        elif answer is None:
            await message.answer("Время на задание истекло.")
            session['userAnswers'][task['number']] = None
        else:
            session['userAnswers'][task['number']] = answer
            await deleteTaskMessages(message, session)
        await processNextTask(message, userId)

    except Exception as e:
        botLogger.error(f"Error sending task {task['number']}: {e}")
        await message.answer(f"Ошибка при отправке задания {task['number']}")
        await finishExam(message, userId, session)


async def deleteTaskMessages(message: Message, session: Dict[str, Any]) -> None:
    for msgId in session.get('messageIds', []):
        try:
            await message.bot.delete_message(message.chat.id, msgId)
        except Exception:
            pass
    session['messageIds'] = []


@router.callback_query(ExamStates.solving_exam, F.data.startswith(f"{SKIP_CALLBACK_PREFIX}:"))
async def skipCurrentTask(callback: CallbackQuery, state: FSMContext) -> None:
    userId = callback.from_user.id
    session = container.answerWaiterService.getExamSession(userId)
    if not session:
        await callback.answer('Сессия не найдена.', show_alert=True)
        return
    if not container.answerWaiterService.hasPendingAnswer(userId):
        await callback.answer('Действие недоступно.', show_alert=True)
        return
    try:
        _, taskNumStr = callback.data.split(':', 1)
        taskNum = int(taskNumStr)
    except (ValueError, AttributeError):
        await callback.answer()
        return
    currentTaskNum = len(session.get('userAnswers', {})) + 1
    if taskNum != currentTaskNum:
        await callback.answer('Кнопка не для текущего задания.', show_alert=True)
        return
    if container.answerWaiterService.setAnswer(userId, SKIP_ANSWER):
        await callback.answer('Задание пропущено.')
    else:
        await callback.answer('Действие недоступно.', show_alert=True)


@router.callback_query(ExamStates.solving_exam, F.data == FINISH_CALLBACK)
async def finishExamEarly(callback: CallbackQuery, state: FSMContext) -> None:
    userId = callback.from_user.id
    session = container.answerWaiterService.getExamSession(userId)
    if not session:
        await callback.answer('Сессия не найдена.', show_alert=True)
        return
    if container.answerWaiterService.setAnswer(userId, FINISH_ANSWER):
        await callback.answer('Экзамен будет завершён.')
    else:
        await callback.answer('Действие недоступно.', show_alert=True)


@router.callback_query(F.data == "back")
async def back_inline(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Вы в главном меню", reply_markup=getRegisteredKeyboard())
    await callback.answer()


@router.message(ExamStates.solving_exam)
async def processAnswer(message: Message, state: FSMContext) -> None:
    userId = message.from_user.id

    if not container.answerWaiterService.hasPendingAnswer(userId):
        await message.answer("Сейчас ответ не требуется. Воспользуйтесь меню.")
        return

    if not container.validationService.validateAnswer(message.text):
        await message.answer("Некорректный ответ. Введите только числа; допускаются точки и дефисы (например: 12-34).")
        return

    container.answerWaiterService.setAnswer(userId, message.text.strip())
    session = container.answerWaiterService.getExamSession(userId)
    if session:
        await deleteTaskMessages(message, session)


async def finishExam(message: Message, userId: int, session: Dict[str, Any]) -> None:
    examData = session['examData']
    examName = session['examName']

    checkResult = container.examService.checkAnswers(examData, session['userAnswers'])

    timeSolve = str(round((datetime.now() - session['startDateTime']).total_seconds() / 60, 2)) + " мин"

    name = container.userRepository.getName(userId) or ""
    surname = container.userRepository.getSurname(userId) or ""
    learningClass = container.userRepository.getClass(userId) or ""

    answersStr = str(session['userAnswers']).replace(chr(9989), '+').replace(chr(10060), '-')

    container.resultRepository.insertResult(
        name, surname, learningClass,
        checkResult['percent'], checkResult['grade'],
        userId, f"{examName}.txt",
        session['timeStart'], timeSolve, answersStr
    )

    resultText = f"Результат {examName}: оценка {checkResult['grade']}\n\n"
    for taskNum, resultSymbol in sorted(checkResult['results'].items()):
        resultText += f"Задание {taskNum} {resultSymbol}\n"

    await message.answer(
        f"Экзамен {examName} завершён. Ниже — сводка результатов. Для нового экзамена откройте меню «Решать экзамены»."
    )
    await message.answer(resultText, reply_markup=getRegisteredKeyboard())

    container.answerWaiterService.removeExamSession(userId)
