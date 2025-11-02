import sys
from pathlib import Path

projectRoot = Path(__file__).parent.parent
sys.path.insert(0, str(projectRoot))

from app.appConfig import RESULT_BASE_PATH, APP_UI_PATH, STYLE_PATH, EXAMS, TEMP, TASKS, QUEST_TIME
from app.appConfig import aboutWindow_UI_PATH, viewExams_UI_PATH, createExams_UI_PATH
from parser.parser import getAnswer
from bot.botRunner import stopBotWrapper as stopBot, startBotWrapper as startBot
import os
import shutil
import threading
from datetime import date
from random import choice

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QWidget
from PyQt5.QtWidgets import QAbstractItemView, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class viewExams(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(viewExams_UI_PATH, self)
        self.setFixedSize(1100, 675)
        self.tableWidget.resizeColumnsToContents()
        self.setStyleSheet(open(str(STYLE_PATH), "r").read())

        self.images = []
        self.currentImageIndex = 0
        self.preview.setAlignment(Qt.AlignCenter)

        self.creatorWindow = createExams()

        self.tableWidget.cellClicked.connect(self.cellWasClicked)

        self.update.clicked.connect(self.updateTable)
        self.right.clicked.connect(self.nextImage)
        self.left.clicked.connect(self.previousImage)
        self.openCreatorBtn.clicked.connect(self.openCreator)
        self.deleteSelectedBtn.clicked.connect(self.deleteSelected)
        self.createRandom.clicked.connect(self.creaternd)

        self.updateTable()

    def creaternd(self):
        self.creatorWindow.createRandom()
        self.creatorWindow.saveExam()
        self.updateTable()

    def openCreator(self):
        self.creatorWindow.show()
        self.close()

    def updateTable(self):
        files = os.listdir(str(EXAMS))

        self.tableWidget.setRowCount(0)
        for i, file_name in enumerate(files):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(file_name))

    def cellWasClicked(self, row:int, column:int):
        cellContent = self.tableWidget.item(row, column).text()


        self.selectedCell = cellContent

        f = open(str(EXAMS / cellContent))
        settings = f.readline()
        lines = f.readlines()
        self.procesExamFile(lines, settings)

    def procesExamFile(self, lines:list, settings:str):
        self.images = []
        self.currentImageIndex = 0

        for line in lines:
            parts = line.strip().split(';')
            imageName = parts[1]
            imagePath = 'tasks/' + f'/{str(parts[4])}' + f'/{imageName}'
            self.images.append(imagePath)

        if self.images:
            self.showImage(0)

    def showImage(self, index: int):
        if 0 <= index < len(self.images):
            pixmap = QPixmap(self.images[index])
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio))
            self.currentImageIndex = index

    def nextImage(self):
        if self.currentImageIndex < len(self.images) - 1:
            self.showImage(self.currentImageIndex + 1)

    def previousImage(self):
        if self.currentImageIndex > 0:
            self.showImage(self.currentImageIndex - 1)

    def deleteSelected(self):
        os.remove(str(EXAMS / self.selectedCell))
        self.updateTable()


class createExams(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(createExams_UI_PATH, self)
        self.setFixedSize(1100, 675)
        self.tableWidget.resizeColumnsToContents()
        self.setStyleSheet(open(str(STYLE_PATH), "r").read())

        self.images = []
        self.currentImageIndex = 0
        self.preview.setAlignment(Qt.AlignCenter)

        self.selectedRow = None
        self.selectedColumn = None

        self.tableWidget.cellClicked.connect(self.cellWasClicked)
        self.tableWidget.cellDoubleClicked.connect(self.cellWasDoubleClicked)

        self.addQuestionBtn.clicked.connect(self.addQuesion)
        self.remoteQuestionBtn.clicked.connect(self.remoteQuestion)
        self.right.clicked.connect(self.nextImage)
        self.left.clicked.connect(self.previousImage)
        self.createRandomBtn.clicked.connect(self.createRandom)
        self.clearTableBtn.clicked.connect(self.clearTemp)
        self.saveExamBtn.clicked.connect(self.saveExam)
        self.nextTopicBtn.clicked.connect(self.nextTopic)
        self.previousTopicBtn.clicked.connect(self.previousTopic)

        self.downloadQuestions()
        self.updateTable()

    def saveExam(self):
        files = os.listdir(str(TEMP))
        count = len(files)
        time = 1 if self.timeAttached.isChecked() else 0
        if self.examName.text():
            f = open(str(EXAMS / f"{self.examName.text()}.txt"), 'w')
        else:
            f = open(str(EXAMS / f"В{len(os.listdir(str(EXAMS)))}.txt"), 'w')

        f.write(f'{count},{time}\n')
        for n, question in enumerate(files):
            egeNo, topicNo = parseQuestion(question)

            answer = ' '.join(getAnswer(egeNo, topicNo).rstrip().replace('<br/>', ' ').split())

            f.write(f'{n + 1};{question};{QUEST_TIME[int(egeNo)]};{answer};kge{egeNo}\n')

        f.close()
        self.clearTemp()
        self.updateTable()

    def updateTable(self):
        files = os.listdir(TEMP)

        files = sorted(files, key=lambda x: (parseQuestion(x)[0], parseQuestion(x)[1]))

        self.tableWidget.setRowCount(0)
        for i, file_name in enumerate(files):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(file_name))

    def cellWasClicked(self, row:int, column:int):
        self.selectedRow = row
        self.selectedColumn = column

    def cellWasDoubleClicked(self, row, column):
        item = self.tableWidget.item(row, column)
        self.selectedColumn = column
        self.selectedRow = row

        parsedItem = parseQuestion(item.text())
        path = f'{TASKS}/kge{parsedItem[0]}/{item.text()}'

        self.previewWidget = QWidget()
        self.previewWidget.setStyleSheet(open(STYLE_PATH, "r").read())
        self.previewWidget.setWindowTitle(f"Предпросмотр задания {item.text()}")
        self.previewWidget.setFixedSize(900, 500)

        label = QLabel(self.previewWidget)
        label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(path)
        label.setPixmap(pixmap.scaled(811, 421, Qt.KeepAspectRatio))

        buttonDelete = QPushButton('Удалить', self.previewWidget)
        buttonCancel = QPushButton('Закрыть', self.previewWidget)
        buttonCancel.clicked.connect(self.previewWidget.close)
        buttonDelete.clicked.connect(self.remoteQuestion)
        buttonDelete.setFixedSize(175, 50)
        buttonCancel.setFixedSize(175, 50)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonCancel)
        buttonLayout.addWidget(buttonDelete)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(buttonLayout)
        self.previewWidget.setLayout(layout)

        self.previewWidget.show()

    def remoteQuestion(self) -> None:
        if self.selectedRow is not None and self.selectedColumn is not None:
            cellContent = self.tableWidget.item(self.selectedRow, self.selectedColumn).text()
            os.remove(str(TEMP / cellContent))
            self.selectedRow = None
            self.selectedColumn = None
        self.updateTable()

    def nextTopic(self):
        if self.numberEdit.text() != '27': self.numberEdit.setText(f'{int(self.numberEdit.text()) + 1}')

        self.images = []
        self.currentImageIndex = 0
        self.downloadQuestions()

    def previousTopic(self):
        if self.numberEdit.text() != '1': self.numberEdit.setText(f'{int(self.numberEdit.text()) - 1}')

        self.images = []
        self.currentImageIndex = 0
        self.downloadQuestions()

    def addQuesion(self):
        if self.numberEdit.text() == '28':
            return
        shutil.copy(str(self.images[self.currentImageIndex]), str(TEMP))
        self.updateTable()

    def createRandom(self):
        self.clearTemp()

        for questionNumber in range(1, 28):
            files = os.listdir(f'tasks/kge{questionNumber}')

            rndImage = choice(files)
            while '.png' not in rndImage:
                rndImage = choice(files)
            self.images.append(rndImage)
            shutil.copy(str(TASKS / f'kge{questionNumber}' / rndImage), str(TEMP))

        self.updateTable()

        if self.images:
            self.showImage(0)
            self.currentImageIndex = 0

    def downloadQuestions(self):
        try:
            if int(self.numberEdit.text()) in range(1, 28):
                questionNumber = self.numberEdit.text()
            else: return
        except:
            return

        for imageName in os.listdir(f'tasks/kge{questionNumber}'):
            if '.png' in imageName:
                imagePath = f'tasks/kge{questionNumber}/{imageName}'
                self.images.append(imagePath)

        if self.images:
            self.showImage(0)

    def showImage(self, index:int):
        if 0 <= index < len(self.images):
            pixmap = QPixmap(self.images[index])
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio))
            self.currentImageIndex = index
            self.curentNumber.setText(self.images[index])

    def nextImage(self):
        if self.currentImageIndex < len(self.images) - 1:
            self.showImage(self.currentImageIndex + 1)

    def previousImage(self):
        if self.currentImageIndex > 0:
            self.showImage(self.currentImageIndex - 1)

    def clearTemp(self):
        files = os.listdir(str(TEMP))
        for i in files:
            os.remove(str(TEMP / i))
        self.numberEdit.setText('1')

        self.updateTable()
        self.images = []
        self.currentImageIndex = 0
        self.downloadQuestions()


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(aboutWindow_UI_PATH, self)
        self.setFixedSize(428, 235)
        self.setStyleSheet(open(str(STYLE_PATH), "r").read())


class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        uic.loadUi(APP_UI_PATH, self)
        self.setFixedSize(910, 700)
        self.setStyleSheet(open(str(STYLE_PATH), "r").read())

        from bot.database.models import getResultSession
        self.resultSessionFactory = getResultSession

        self.bot_thread = None
        self.hn = False
        self.std = False

        self.upload.clicked.connect(self.selectData)
        self.restart.clicked.connect(self.botRestart)
        self.stop.clicked.connect(self.botStop)
        self.viewExams.clicked.connect(self.openViewExamWindow)
        self.createExamsBtn.clicked.connect(self.openCreateExamsWindow)
        self.openAboutBtn.clicked.connect(self.openAboutWindow)

        self.hideNoneCB.stateChanged.connect(self.hideNone)
        self.showTodaysCB.stateChanged.connect(self.showTodays)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setCurrentIndex(QModelIndex())

        self.createExamsWindow = None

        self.selectData()

    def selectData(self) -> None:
        from bot.repositories.resultRepository import ResultRepository
        resultRepo = ResultRepository()
        results = resultRepo.getAllResults()
        self.res = [
            (
                r.id, r.name, r.surname, r.class_name, r.percent, r.grade,
                r.user_id, r.question, r.time_start, r.time_solve, r.answers
            )
            for r in results
        ]
        self.res.sort(key=lambda x: x[0], reverse=True)
        self.view()

    def view(self):
        self.tableWidget.setRowCount(0)

        data = self.res

        if self.hn:
            data = [i for i in self.res if None not in i]

        if self.std:
            data = [i for i in self.res if i[8] is not None and date.today().strftime('%d.%m.%Y') in i[8]]

        for i, row in enumerate(data):
            self.tableWidget.insertRow(i)
            for j, elem in enumerate(row):
                if type(elem) == str and '{1' in elem:
                    elem = elem.replace('{', '').replace('}', '').replace('+', chr(9989)).replace('-', chr(10060))

                item = QTableWidgetItem(str(elem))
                item.setToolTip(str(elem))
                self.tableWidget.setItem(i, j, item)

    def botStop(self):
        stopBot()
        self.bot_thread = None

    def botRestart(self):
        stopBot()

        if self.bot_thread is not None:
            self.bot_thread.join()
        self.bot_thread = threading.Thread(target=startBot)
        self.bot_thread.start()

    def hideNone(self, state):
        self.hn = (state == Qt.Checked)
        self.view()

    def showTodays(self, state):
        self.std = (state == Qt.Checked)
        self.view()

    def closeEvent(self, event) -> None:

        if self.bot_thread is not None:
            msg = QMessageBox()
            msg.setWindowTitle("Внимание!")
            buttonAceptar = msg.addButton('Да', QMessageBox.YesRole)
            buttonCancelar = msg.addButton('Нет', QMessageBox.RejectRole)
            msg.setDefaultButton(buttonAceptar)
            msg.setText("Сейчас запущен бот, вы хотите его остановить перед закрытием?")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

            if msg.clickedButton() == buttonAceptar:
                stopBot()
                self.bot_thread.join()
                exit(0)
            elif msg.clickedButton() == buttonCancelar:
                event.accept()

        if self.createExamsWindow is not None: createExams.clearTemp(self.createExamsWindow)

    def openViewExamWindow(self):
        self.examWindow = viewExams()
        self.examWindow.show()

    def openCreateExamsWindow(self):
        self.createExamsWindow = createExams()
        self.createExamsWindow.show()

    def openAboutWindow(self):
        self.aboutWindow = AboutWindow()
        self.aboutWindow.show()


def parseQuestion(question:str) -> tuple:
    egeNo = question.split('(')[0].replace('kge', '')
    topicNo = question.split('(')[1][:question.split('(')[1].index(')')]
    return int(egeNo), int(topicNo)


def openApp():
    appConfig = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(appConfig.exec_())


if __name__ == "__main__":
    openApp()
