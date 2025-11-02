import asyncio
import threading
from bot.botMainAiogram import startBot, stopBot


_loop = None
_thread = None
_task = None


def _runBotInThread() -> None:
    global _loop, _task
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _task = _loop.create_task(startBot())
    _loop.run_forever()


def startBotWrapper() -> None:
    global _thread
    if _thread is None or not _thread.is_alive():
        _thread = threading.Thread(target=_runBotInThread, daemon=True)
        _thread.start()


def stopBotWrapper() -> None:
    global _loop, _task, _thread

    if _loop and _loop.is_running():
        if _task:
            _task.cancel()
        _loop.call_soon_threadsafe(_loop.stop)

    if _thread and _thread.is_alive():
        _thread.join(timeout=5)

