import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from bot.botConfig import BOT_TOKEN
from bot.database.migrations import initDatabasesWrapper as initDatabases
from bot.handlers import commonHandlers, registrationHandlers, examHandlers
from utils.logger import botLogger

logging.basicConfig(level=logging.INFO)

bot = None
dp = None


async def startBot() -> None:
    global bot, dp

    try:
        initDatabases()
        botLogger.info("Databases initialized")

        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())

        dp.include_router(commonHandlers.router)
        dp.include_router(registrationHandlers.router)
        dp.include_router(examHandlers.router)

        botLogger.info("Bot starting...")
        await dp.start_polling(bot)

    except Exception as e:
        botLogger.error(f"Error starting bot: {e}")
        raise
    finally:
        if bot:
            await bot.session.close()


async def stopBot() -> None:
    global bot, dp

    if dp:
        await dp.stop_polling()
    if bot:
        await bot.session.close()

    botLogger.info("Bot stopped")


def runBot() -> None:
    try:
        asyncio.run(startBot())
    except KeyboardInterrupt:
        botLogger.info("Bot stopped by user")
    except Exception as e:
        botLogger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    runBot()
