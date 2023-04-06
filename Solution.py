import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDockWidget, QApplication, QMainWindow, QPushButton, QLabel, QTimeEdit, QListWidget
from PyQt5.QtWidgets import QCalendarWidget, QFileDialog, QTableWidgetItem


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI1.ui', self)
        self.connection = sqlite3.connect("films_db.sqlite")
        self.pushButton.clicked.connect(self.select_data)

        self.select_data()

    def select_data(self):
        query = ""
        query_year, query_title, query_duration = "", "", ""
        if not self.lineEdit_year.text() and not self.lineEdit_title.text() and not self.lineEdit_duration.text():
            query = "SELECT * FROM films"
        if self.lineEdit_year.text():
            query_year = f"SELECT * FROM Films WHERE year {self.lineEdit_year.text()}" 
            print(query_year)
        if self.lineEdit_duration.text():
            query_duration = f"duration {self.lineEdit_duration.text()}"
            print(query_duration)
        if self.lineEdit_title.text():
            query_title = f"title {self.lineEdit_title.text()}"
            print(query_title)
        if query_year:
            query += query_year
        if query_duration:
            query += " AND " + query_duration
        if query_title:
            query += " AND " + query_title
        print(query)
        res = self.connection.cursor().execute(query).fetchall()


        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)

        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.connection.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec_())
    