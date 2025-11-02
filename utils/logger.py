import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setupLogger(name: str, logFile: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    logDir = Path("logs")
    logDir.mkdir(exist_ok=True)

    fileHandler = RotatingFileHandler(
        logDir / logFile,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    fileHandler.setLevel(level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    fileHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    return logger


botLogger = setupLogger('bot', 'bot.log')
appLogger = setupLogger('app', 'app.log')
dbLogger = setupLogger('db', 'db.log')
