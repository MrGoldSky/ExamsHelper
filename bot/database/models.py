from sqlalchemy import Column, Integer, String, Float, DateTime, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
from bot.botConfig import TG_BASE_PATH, RESULT_BASE_PATH

Base = declarative_base()


class TelegramUser(Base):
    __tablename__ = 'telegram_users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    class_name = Column(String(20), nullable=True)
    status = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )


class ExamResult(Base):
    __tablename__ = 'exam_results'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    class_name = Column(String(20), nullable=False)
    percent = Column(Float, nullable=False)
    grade = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    question = Column(String(100), nullable=False, index=True)
    time_start = Column(String(50), nullable=False)
    time_solve = Column(String(50), nullable=False)
    answers = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_user_question', 'user_id', 'question'),
        Index('idx_user_id', 'user_id'),
        Index('idx_question', 'question'),
        Index('idx_created_at', 'created_at'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )


def getTelegramEngine():
    dbPath = TG_BASE_PATH
    dbPath.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f'sqlite:///{dbPath}', echo=False, pool_pre_ping=True)


def getResultEngine():
    dbPath = RESULT_BASE_PATH
    dbPath.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f'sqlite:///{dbPath}', echo=False, pool_pre_ping=True)


def getTelegramSession():
    engine = getTelegramEngine()
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def getResultSession():
    engine = getResultEngine()
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def initDatabases() -> None:
    telegramEngine = getTelegramEngine()
    resultEngine = getResultEngine()

    Base.metadata.create_all(telegramEngine, tables=[TelegramUser.__table__])
    Base.metadata.create_all(resultEngine, tables=[ExamResult.__table__])
