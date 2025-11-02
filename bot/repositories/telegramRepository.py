from typing import Optional
from sqlalchemy.orm import Session
from bot.database.models import TelegramUser, getTelegramSession
from bot.repositories.baseRepository import BaseRepository
from utils.logger import dbLogger


class TelegramRepository(BaseRepository[TelegramUser]):
    def __init__(self) -> None:
        super().__init__(getTelegramSession)

    def create(self, entity: TelegramUser) -> Optional[TelegramUser]:
        try:
            with self.getSession() as session:
                session.add(entity)
                session.flush()
                return entity
        except Exception as e:
            dbLogger.error(f"Error creating user: {e}")
            return None

    def getById(self, userId: int) -> Optional[TelegramUser]:
        try:
            with self.getSession() as session:
                return session.query(TelegramUser).filter(TelegramUser.user_id == userId).first()
        except Exception as e:
            dbLogger.error(f"Error getting user by id: {e}")
            return None

    def update(self, entity: TelegramUser) -> bool:
        try:
            with self.getSession() as session:
                session.merge(entity)
                return True
        except Exception as e:
            dbLogger.error(f"Error updating user: {e}")
            return False

    def delete(self, userId: int) -> bool:
        try:
            with self.getSession() as session:
                user = session.query(TelegramUser).filter(TelegramUser.user_id == userId).first()
                if user:
                    session.delete(user)
                    return True
                return False
        except Exception as e:
            dbLogger.error(f"Error deleting user: {e}")
            return False

    def createUser(self, userId: int) -> bool:
        user = TelegramUser(user_id=userId)
        return self.create(user) is not None

    def updateName(self, userId: int, name: str) -> bool:
        user = self.getById(userId)
        if not user:
            return False
        user.name = name
        return self.update(user)

    def updateSurname(self, userId: int, surname: str) -> bool:
        user = self.getById(userId)
        if not user:
            return False
        user.surname = surname
        return self.update(user)

    def updateClass(self, userId: int, className: str) -> bool:
        user = self.getById(userId)
        if not user:
            return False
        user.class_name = className
        return self.update(user)

    def getName(self, userId: int) -> Optional[str]:
        user = self.getById(userId)
        return user.name if user else None

    def getSurname(self, userId: int) -> Optional[str]:
        user = self.getById(userId)
        return user.surname if user else None

    def getClass(self, userId: int) -> Optional[str]:
        user = self.getById(userId)
        return user.class_name if user else None

    def userExists(self, userId: int) -> bool:
        return self.getById(userId) is not None

