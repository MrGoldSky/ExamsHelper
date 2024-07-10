import sqlite3

from app.appConfig import RESULT_BASE_PATH, APP_UI_PATH, STYLE_PATH, EXAMS, TEMP, TASKS, viewExams_UI_PATH, createExams_UI_PATH
from bot.botMain import stopBot, startBot

import sys
import os
import shutil
import threading

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QWidget
from PyQt5.QtWidgets import QAbstractItemView, QPushButton, QVBoxLayout
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QPixmap


class viewExams(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(viewExams_UI_PATH, self)
        self.setFixedSize(900, 540)
        self.tableWidget.resizeColumnsToContents()
        self.setStyleSheet(open(STYLE_PATH, "r").read())
        
        self.images = []
        self.currentImageIndex = 0
        
        self.tableWidget.cellClicked.connect(self.cellWasClicked)
        
        # Подключение кнопок
        self.update.clicked.connect(self.updateTable)
        self.right.clicked.connect(self.nextImage)
        self.left.clicked.connect(self.previousImage)
        self.openCreatorBtn.clicked.connect(self.openCreator)
        self.updateTable()

    def openCreator(self):
        self.creatorWindow = createExams()
        self.creatorWindow.show()
        self.close()


    def updateTable(self): # Обновление данных таблицы
        files = os.listdir(EXAMS)

        self.tableWidget.setRowCount(0) # Отчистка таблицы
        for i, file_name in enumerate(files):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(file_name))

    def cellWasClicked(self, row, column): # Обработчик выбора ячейки
        cellContent = self.tableWidget.item(row, column).text()

        # Загрузка содержимого файла
        f = open(EXAMS + cellContent)
        settings = f.readline()
        lines = f.readlines()
        self.procesExamFile(lines, settings)

    def procesExamFile(self, lines, settings):
        self.images = []
        self.currentImageIndex = 0

        # Обработка первой строки
        # settings = lines[0].split(',')
        settingsInfo = f"Кол. вопросов: {settings[0]}, Вкл. время теста: {settings[1]}, Отк. кн. назад: {settings[2]}, Вкл. кн. помощь: {settings[3]}, Вкл. право на ошибку: {settings[4]}, Вкл. генератор варианта: {settings[5].strip()}"
        # QMessageBox.information(self, "Настройки теста", settingsInfo)

        # Cохранение путей к картинкам заданий
        for line in lines:
            parts = line.strip().split(';')
            imageName = parts[1]
            imagePath = 'tasks/' + f'/{str(parts[4])}' + f'/{imageName}'
            self.images.append(imagePath)

        # Отображение первого изображения
        if self.images:
            self.showImage(0)

    def showImage(self, index): # Отображение картинки с номером index
        if 0 <= index < len(self.images):
            pixmap = QPixmap(self.images[index])
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), aspectRatioMode=1))
            self.currentImageIndex = index

    def nextImage(self): # Отображение следующей картинки
        if self.currentImageIndex < len(self.images) - 1:
            self.showImage(self.currentImageIndex + 1)

    def previousImage(self): # Отображение предыдущей картинки
        if self.currentImageIndex > 0:
            self.showImage(self.currentImageIndex - 1)


class createExams(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(createExams_UI_PATH, self)
        self.setFixedSize(1100, 675)
        self.tableWidget.resizeColumnsToContents()
        self.setStyleSheet(open(STYLE_PATH, "r").read())
        
        self.images = []
        self.currentImageIndex = 0
        
        self.selectedRow = None
        self.selectedColumn = None
        
        self.tableWidget.cellClicked.connect(self.cellWasClicked)
        
        # Подключение кнопок
        self.addQuestionBtn.clicked.connect(self.addQuesion)
        self.remoteQuestionBtn.clicked.connect(self.remoteQuestion)
        self.right.clicked.connect(self.nextImage)
        self.left.clicked.connect(self.previousImage)
        self.createRandomBtn.clicked.connect(self.createRandom)
        self.createExamBtn.clicked.connect(self.createExam)
        self.clearTableBtn.clicked.connect(self.clearTemp)
        self.downloadQuestions()
        self.updateTable()

    def updateTable(self): # Обновление данных таблицы
        files = os.listdir(TEMP)
        
        self.tableWidget.setRowCount(0) # Отчистка таблицы
        for i, file_name in enumerate(files):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(file_name))

    def cellWasClicked(self, row, column): # Обработчик выбора ячейки
        self.selectedRow = row
        self.selectedColumn = column
    
    # Удаление выбранной карточки
    def remoteQuestion(self): 
        if self.selectedRow is not None and self.selectedColumn is not None: # Проверка, что удаляемая карточка выбрана
            cellContent = self.tableWidget.item(self.selectedRow, self.selectedColumn).text()
            os.remove(TEMP+f'/{cellContent}')
            self.selectedRow = None
            self.selectedColumn = None
        self.updateTable()

    def addQuesion(self):
        shutil.copy(f'{self.images[self.currentImageIndex]}', TEMP) # Копируем карточку в временное хранилище
        self.updateTable() #Обновляем таблицу карточек
        self.images = []
        self.currentImageIndex = 0
        
        # Загружаем карточки следующего номера
        self.numberEdit.setText(f'{int(self.numberEdit.text()) + 1}')
        self.downloadQuestions() 

    def createRandom(self):
        ...
        self.updateTable()

    def createExam(self):
        ...
        self.updateTable()

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

        # Отображение первого изображения
        if self.images:
            self.showImage(0)

    def showImage(self, index): # Отображение картинки с номером index
        if 0 <= index < len(self.images):
            pixmap = QPixmap(self.images[index])
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), aspectRatioMode=1))
            self.currentImageIndex = index

    def nextImage(self): # Отображение следующей картинки
        if self.currentImageIndex < len(self.images) - 1:
            self.showImage(self.currentImageIndex + 1)

    def previousImage(self): # Отображение предыдущей картинки
        if self.currentImageIndex > 0:
            self.showImage(self.currentImageIndex - 1)

    def clearTemp(self): # Отчистка папки temp
        files = os.listdir(TEMP)
        for i in files:
            os.remove(f'{TEMP}/{i}')
        self.numberEdit.setText('1') # Переключаем на карточку с 1 заданием
        
        # Обновляем таблицу и показ карточек
        self.updateTable()
        self.images = []
        self.currentImageIndex = 0
        self.downloadQuestions()


class MainWindow(QMainWindow):
    def __init__(self):
        # Подключение UI
        super().__init__()
        uic.loadUi(APP_UI_PATH, self)
        self.setFixedSize(910, 700)
        self.setStyleSheet(open(STYLE_PATH, "r").read())
        
        # Подключение к бд
        self.con = sqlite3.connect(RESULT_BASE_PATH)
        self.cur = self.con.cursor()
        
        # Начальные значения
        self.bot_thread = None
        self.hn = False
        
        # Подключение кнопок
        self.upload.clicked.connect(self.selectData)
        self.restart.clicked.connect(self.botRestart)
        self.stop.clicked.connect(self.botStop)
        self.viewExams.clicked.connect(self.openViewExamWindow)
        self.createExamsBtn.clicked.connect(self.openCreateExamsWindow)
        
        # Подключение чек боксов
        self.hideNoneCB.stateChanged.connect(self.hideNone)
        
        # Настройки виджета таблицы
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setCurrentIndex(QModelIndex())
        
        # CreateExams ещё не открыто
        self.createExamsWindow = None
        
        self.selectData()

    def selectData(self): # Вытягивание данных из бд
        self.res = self.cur.execute(f"""SELECT * from base""").fetchall()
        self.res.sort(key=lambda x: x[0], reverse=True)
        self.view()

    def view(self): # Ввод данных в таблицу и настройка подсказок
        self.tableWidget.setRowCount(0)  # Очистка таблицы
        
        data = self.res
        
        if self.hn: # Если выбран режим без None
            data = [i for i in self.res if None not in i]
        
        for i, row in enumerate(data): # Ввод данных в таблицу
            self.tableWidget.insertRow(i)
            for j, elem in enumerate(row):
                if type(elem) == str and '{1' in elem:
                    elem = elem.replace('{', '').replace('}', '').replace('+', chr(9989)).replace('-', chr(10060))
                
                item = QTableWidgetItem(str(elem))
                item.setToolTip(str(elem))
                self.tableWidget.setItem(i, j, item)

    def botStop(self): # Остановка бота
        stopBot()
        self.bot_thread = None

    def botRestart(self): # Перезапуск бота
        stopBot()
        # Бот запускается в отдельном потоке
        if self.bot_thread is not None:
            self.bot_thread.join()  # Ожидаем завершения потока
        self.bot_thread = threading.Thread(target=startBot)
        self.bot_thread.start()

    def hideNone(self, state):
        self.hn = (state == Qt.Checked)
        self.view()

    def closeEvent(self, event): # Обработка закрытия журнала
        # Вывод диалогового окна, если бот запущен во время закрытия
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
                self.bot_thread.join()  # Ожидаем завершения потока
                self.con.close()
            elif msg.clickedButton() == buttonCancelar:
                event.accept()
        
        
        if self.createExamsWindow is not None: createExams.clearTemp(self.createExamsWindow)

    def openViewExamWindow(self):
        self.examWindow = viewExams()
        self.examWindow.show()

    def openCreateExamsWindow(self):
        self.createExamsWindow = createExams()
        self.createExamsWindow.show()

def openApp(): # Открытие журнала
    appConfig = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(appConfig.exec_())
