from pathlib import Path
from typing import Dict, List, Optional, Any
from bot.botConfig import EXAMS, TASKS
from utils.logger import botLogger


class ExamService:
    def __init__(self) -> None:
        self.examsPath = EXAMS if isinstance(EXAMS, Path) else Path(EXAMS)
        self.tasksPath = TASKS if isinstance(TASKS, Path) else Path(TASKS)

    def getAvailableExams(self) -> List[str]:
        try:
            if isinstance(self.examsPath, str):
                self.examsPath = Path(self.examsPath)
            return [f.stem for f in self.examsPath.glob("*.txt")]
        except OSError as e:
            botLogger.error(f"Error getting exams list: {e}")
            return []

    def loadExam(self, examName: str) -> Optional[Dict[str, Any]]:
        try:
            if isinstance(self.examsPath, str):
                self.examsPath = Path(self.examsPath)
            examFile = self.examsPath / f"{examName}.txt"
            if not examFile.exists():
                botLogger.warning(f"Exam file not found: {examFile}")
                return None

            with open(examFile, 'r', encoding='utf-8') as f:
                settingsLine = f.readline().strip()
                settings = settingsLine.split(',')

                tasks = []
                totalTime = 0
                for line in f:
                    if line.strip():
                        parts = line.strip().split(';')
                        if len(parts) >= 5:
                            taskNum = int(parts[0])
                            taskFile = parts[1]
                            timeLimit = int(parts[2])
                            answer = parts[3]
                            taskFolder = parts[4]

                            totalTime += timeLimit
                            tasks.append({
                                'number': taskNum,
                                'file': taskFile,
                                'time_limit': timeLimit,
                                'answer': answer,
                                'folder': taskFolder
                            })

                return {
                    'name': examName,
                    'count': int(settings[0]),
                    'time_enabled': int(settings[1]) == 1,
                    'tasks': tasks,
                    'total_time': totalTime
                }
        except (FileNotFoundError, IOError, ValueError, IndexError) as e:
            botLogger.error(f"Error loading exam {examName}: {e}")
            return None

    def getTaskImagePath(self, taskFolder: str, taskFile: str) -> Optional[Path]:
        try:
            if isinstance(self.tasksPath, str):
                self.tasksPath = Path(self.tasksPath)
            imagePath = self.tasksPath / taskFolder / taskFile
            if imagePath.exists():
                return imagePath
            return None
        except Exception as e:
            botLogger.error(f"Error getting task image path: {e}")
            return None

    def getTaskAdditionalFiles(self, taskFolder: str, taskFile: str) -> List[Path]:
        try:
            if isinstance(self.tasksPath, str):
                self.tasksPath = Path(self.tasksPath)
            folderPath = self.tasksPath / taskFolder
            if not folderPath.exists():
                return []

            baseName = taskFile.rsplit('.', 1)[0] if '.' in taskFile else taskFile
            egeNo = taskFolder.replace('kge', '')
            maskPrefix = f"{egeNo}-{baseName.split('(')[1].split(')')[0] if '(' in baseName else ''}"

            additionalFiles = []
            for file in folderPath.iterdir():
                if file.name.startswith(maskPrefix) and file.name != taskFile:
                    additionalFiles.append(file)

            return additionalFiles
        except Exception as e:
            botLogger.error(f"Error getting additional files: {e}")
            return []

    def calculateGrade(self, percent: float) -> int:
        if percent >= 85:
            return 5
        elif percent >= 70:
            return 4
        elif percent >= 50:
            return 3
        elif percent >= 40:
            return 2
        else:
            return 1

    def checkAnswers(self, examData: Dict[str, Any], userAnswers: Dict[int, str]) -> Dict[str, Any]:
        correctCount = 0
        totalCount = len(examData['tasks'])
        results = {}

        for task in examData['tasks']:
            taskNum = task['number']
            correctAnswer = task['answer'].strip()
            userAnswer = userAnswers.get(taskNum, '').strip() if userAnswers.get(taskNum) else ''

            if userAnswer and userAnswer == correctAnswer:
                correctCount += 1
                results[taskNum] = chr(9989)
            else:
                results[taskNum] = chr(10060)

        percent = round((correctCount / totalCount) * 100, 2) if totalCount > 0 else 0
        grade = self.calculateGrade(percent)

        return {
            'correct': correctCount,
            'total': totalCount,
            'percent': percent,
            'grade': grade,
            'results': results
        }

