from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_class = State()


class ExamStates(StatesGroup):
    waiting_for_exam_selection = State()
    solving_exam = State()
    waiting_for_answer = State()
