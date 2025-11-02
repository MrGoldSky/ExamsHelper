from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from bot.database.models import ExamResult, getResultSession
from bot.repositories.baseRepository import BaseRepository
from utils.logger import dbLogger


class ResultRepository(BaseRepository[ExamResult]):
    def __init__(self) -> None:
        super().__init__(getResultSession)

    def create(self, entity: ExamResult) -> Optional[ExamResult]:
        try:
            with self.getSession() as session:
                session.add(entity)
                session.flush()
                return entity
        except Exception as e:
            dbLogger.error(f"Error creating result: {e}")
            return None

    def getById(self, resultId: int) -> Optional[ExamResult]:
        try:
            with self.getSession() as session:
                return session.query(ExamResult).filter(ExamResult.id == resultId).first()
        except Exception as e:
            dbLogger.error(f"Error getting result by id: {e}")
            return None

    def update(self, entity: ExamResult) -> bool:
        try:
            with self.getSession() as session:
                session.merge(entity)
                return True
        except Exception as e:
            dbLogger.error(f"Error updating result: {e}")
            return False

    def delete(self, resultId: int) -> bool:
        try:
            with self.getSession() as session:
                result = session.query(ExamResult).filter(ExamResult.id == resultId).first()
                if result:
                    session.delete(result)
                    return True
                return False
        except Exception as e:
            dbLogger.error(f"Error deleting result: {e}")
            return False

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
        result = ExamResult(
            name=name,
            surname=surname,
            class_name=learningClass,
            percent=percent,
            grade=grade,
            user_id=userId,
            question=question,
            time_start=timeStart,
            time_solve=timeSolve,
            answers=answers
        )
        return self.create(result) is not None

    def getMaxGrade(self, userId: int, question: str) -> Optional[int]:
        try:
            with self.getSession() as session:
                result = session.query(func.max(ExamResult.grade)).filter(
                    ExamResult.user_id == userId,
                    ExamResult.question == question
                ).scalar()
                return int(result) if result is not None else None
        except Exception as e:
            dbLogger.error(f"Error getting max grade: {e}")
            return None

    def getMaxPercent(self, userId: int, question: str) -> Optional[float]:
        try:
            with self.getSession() as session:
                result = session.query(func.max(ExamResult.percent)).filter(
                    ExamResult.user_id == userId,
                    ExamResult.question == question
                ).scalar()
                return float(result) if result is not None else None
        except Exception as e:
            dbLogger.error(f"Error getting max percent: {e}")
            return None

    def getCount(self, userId: int, question: str) -> int:
        try:
            with self.getSession() as session:
                return session.query(ExamResult).filter(
                    ExamResult.user_id == userId,
                    ExamResult.question == question
                ).count()
        except Exception as e:
            dbLogger.error(f"Error getting count: {e}")
            return 0

    def getAllResults(self) -> List[ExamResult]:
        try:
            with self.getSession() as session:
                return session.query(ExamResult).order_by(ExamResult.id.desc()).all()
        except Exception as e:
            dbLogger.error(f"Error getting all results: {e}")
            return []

