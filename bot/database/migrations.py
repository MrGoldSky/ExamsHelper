from bot.database.models import initDatabases
from utils.logger import dbLogger


def initDatabasesWrapper() -> None:
    try:
        initDatabases()
        dbLogger.info("All databases initialized successfully")
    except Exception as e:
        dbLogger.error(f"Error initializing databases: {e}")
        raise

init_databases = initDatabasesWrapper
