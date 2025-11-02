from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generic, TypeVar, Optional, Any
from sqlalchemy.orm import Session
from utils.logger import dbLogger

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    def __init__(self, sessionFactory) -> None:
        self._sessionFactory = sessionFactory

    @contextmanager
    def getSession(self) -> Session:
        session = self._sessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            dbLogger.error(f"Database error in repository: {e}")
            raise
        finally:
            session.close()

    @abstractmethod
    def create(self, entity: T) -> Optional[T]:
        pass

    @abstractmethod
    def getById(self, entityId: Any) -> Optional[T]:
        pass

    @abstractmethod
    def update(self, entity: T) -> bool:
        pass

    @abstractmethod
    def delete(self, entityId: Any) -> bool:
        pass

