import sqlite3
from app.appConfig import RESULT_BASE_PATH, UI_PATH, STYLE_PATH
from bot.botMain import stopBot, startBot
import sys
import threading

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import QModelIndex


class DBSample(QMainWindow):
    def __init__(self):
        # Подключение UI
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.setFixedSize(910, 700)
        self.setStyleSheet(open(STYLE_PATH, "r").read())
        
        # Подключение к бд
        self.con = sqlite3.connect(RESULT_BASE_PATH)
        self.cur = self.con.cursor()
        
        # Начальные значения
        self.bot_thread = None
        self.firstView = True
        
        # Подключение кнопок
        self.upload.clicked.connect(self.selectData)
        self.restart.clicked.connect(self.botRestart)
        self.stop.clicked.connect(self.botStop)
        
        # Настройки виджета таблицы
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setCurrentIndex(QModelIndex())
        
        self.selectData()

    def selectData(self): # Вытягивание данных из бд
        self.res = self.cur.execute(f"""SELECT * from base""").fetchall()
        self.res.sort(key=lambda x: x[0], reverse=True)
        self.view()

    def view(self): # Ввод данных в таблицу и настройка подсказок
        for i, row in enumerate(self.res):
            if i > self.tableWidget.rowCount() or self.firstView is True:
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                item = QTableWidgetItem(str(elem))
                item.setToolTip(str(elem))
                self.tableWidget.setItem(i, j, item)
        self.firstView = False

    def botStop(self): # Остановка бота
        stopBot()
        self.bot_thread = None

    def botRestart(self): # Перезапуск бота
        stopBot()
        # Бот запускается в отдельном потоке
        if self.bot_thread is not None: self.bot_thread.join() # Ожидаем завершения потока
        self.bot_thread = threading.Thread(target=startBot)
        self.bot_thread.start()

    def closeEvent(self, event): # Обработка закрытия журнала
        # Вывод диологового окна, если бот запущен во время закрытия
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

def openApp(): # Открытие журнала
    appConfig = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(appConfig.exec_())
    