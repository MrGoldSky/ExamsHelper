import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "5806618918:AAGPM8wm52hyM8kXA9mRihxlKfkZtYrQAZ4")  # Токен бота
TG_BASE_PATH = os.getenv("TG_BASE_PATH", "results/base/result_base.sqlite")  # Путь к базе данных бота
RESULT_BASE_PATH = os.getenv("RESULT_BASE_PATH", "results/base/result_base.sqlite")  # Путь к базе данных результатов
TASKS = "tasks/" #Путь к карточкам
EXAMS = "exams/" #Путь к txt вариантам
URL = 'https://api.telegram.org/bot' #Telegram url
RESULT_PATH = "results/text/" #Путь к txt результатам
APP_UI_PATH = 'app/ui/app.ui'
viewExams_UI_PATH = 'app/ui/viewExams.ui'
