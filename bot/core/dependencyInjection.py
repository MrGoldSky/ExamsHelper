from typing import Protocol
from bot.core.interfaces import IUserRepository, IResultRepository, IExamService, IValidationService
from bot.repositories.telegramRepository import TelegramRepository
from bot.repositories.resultRepository import ResultRepository
from bot.services.examService import ExamService
from bot.services.validationService import ValidationService
from bot.services.answerWaiterService import AnswerWaiterService


class ServiceContainer:
    def __init__(self) -> None:
        self._userRepository: IUserRepository = TelegramRepository()
        self._resultRepository: IResultRepository = ResultRepository()
        self._examService: IExamService = ExamService()
        self._validationService: IValidationService = ValidationService()
        self._answerWaiterService: AnswerWaiterService = AnswerWaiterService()

    @property
    def userRepository(self) -> IUserRepository:
        return self._userRepository

    @property
    def resultRepository(self) -> IResultRepository:
        return self._resultRepository

    @property
    def examService(self) -> IExamService:
        return self._examService

    @property
    def validationService(self) -> IValidationService:
        return self._validationService

    @property
    def answerWaiterService(self) -> AnswerWaiterService:
        return self._answerWaiterService


_container: ServiceContainer | None = None


def getContainer() -> ServiceContainer:
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container

