import os
from pathlib import Path

RESULT_BASE_PATH = Path(os.getenv("RESULT_BASE_PATH", "results/base/result_base.sqlite"))
TASKS = Path("tasks")
EXAMS = Path("exams")
RESULT_PATH = Path("results/text")
APP_UI_PATH = Path('app/ui/app.ui')
STYLE_PATH = Path("app/ui/styles/style.css")
TEMP = Path('app/temp')
QUEST_TIME = {1:3, 2:3, 3:3, 4:2, 5:4, 6:4, 7:5, 8:4, 9:6, 10:3,
             11:3, 12:6, 13:3, 14:3, 15:3, 16:5, 17:14, 18:6, 19:6,
             20:8, 21:11, 22:7, 23:8, 24:18, 25:20, 26:35, 27:35}
viewExams_UI_PATH = Path('app/ui/viewExams.ui')
createExams_UI_PATH = Path('app/ui/createExams.ui')
aboutWindow_UI_PATH = Path('app/ui/about.ui')
