from abc import ABC
from typing import Optional, List, Protocol, Any, Dict
from bot.database.models import TelegramUser, ExamResult


class IRepository(ABC):
    pass


class IUserRepository(Protocol):
    def createUser(self, userId: int) -> bool:
        ...

    def updateName(self, userId: int, name: str) -> bool:
        ...

    def updateSurname(self, userId: int, surname: str) -> bool:
        ...

    def updateClass(self, userId: int, className: str) -> bool:
        ...

    def getName(self, userId: int) -> Optional[str]:
        ...

    def getSurname(self, userId: int) -> Optional[str]:
        ...

    def getClass(self, userId: int) -> Optional[str]:
        ...

    def userExists(self, userId: int) -> bool:
        ...


class IResultRepository(Protocol):
    def insertResult(
        self,
        name: str,
        surname: str,
        learningClass: str,
        percent: float,
        grade: int,
        userId: int,
        question: str,
        timeStart: str,
        timeSolve: str,
        answers: str
    ) -> bool:
        ...

    def getMaxGrade(self, userId: int, question: str) -> Optional[int]:
        ...

    def getMaxPercent(self, userId: int, question: str) -> Optional[float]:
        ...

    def getCount(self, userId: int, question: str) -> int:
        ...

    def getAllResults(self) -> List[ExamResult]:
        ...


class IExamService(Protocol):
    def getAvailableExams(self) -> List[str]:
        ...

    def loadExam(self, examName: str) -> Optional[Dict[str, Any]]:
        ...

    def getTaskImagePath(self, taskFolder: str, taskFile: str) -> Optional[Any]:
        ...

    def getTaskAdditionalFiles(self, taskFolder: str, taskFile: str) -> List[Any]:
        ...

    def calculateGrade(self, percent: float) -> int:
        ...

    def checkAnswers(self, examData: Dict[str, Any], userAnswers: Dict[int, str]) -> Dict[str, Any]:
        ...


class IValidationService(Protocol):
    def validateName(self, name: str) -> bool:
        ...

    def validateSurname(self, surname: str) -> bool:
        ...

    def validateClass(self, className: str) -> bool:
        ...

    def validateAnswer(self, answer: str) -> bool:
        ...

    def validateExamName(self, examName: str, availableExams: List[str]) -> Optional[str]:
        ...
