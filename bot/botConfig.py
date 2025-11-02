import os
from pathlib import Path
from typing import Iterator, Tuple


def _iter_env_lines(env_path: Path) -> Iterator[Tuple[str, str]]:
    with env_path.open("r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            yield key.strip(), value.strip()


def _load_env_file() -> None:
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    if not env_path.exists():
        return

    for key, value in _iter_env_lines(env_path):
        os.environ.setdefault(key, value)


_load_env_file()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN.upper() == "YOUR_BOT_TOKEN":
    raise RuntimeError(
        "Переменная окружения BOT_TOKEN не установлена или содержит плейсхолдер. "
        "Создайте файл .env (по образцу .env.example) или задайте значение переменной окружения."
    )

TG_BASE_PATH = Path(os.getenv("TG_BASE_PATH", "results/base/telegram_db.sqlite"))
RESULT_BASE_PATH = Path(os.getenv("RESULT_BASE_PATH", "results/base/result_base.sqlite"))
TASKS = Path("tasks")
EXAMS = Path("exams")
RESULT_PATH = Path("results/text")
