# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Mr_GoldSky_\Desktop\Git\UI1.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(762, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(230, 20, 511, 511))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 230, 211, 51))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 47, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 80, 61, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 140, 47, 13))
        self.label_3.setObjectName("label_3")
        self.lineEdit_year = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_year.setGeometry(QtCore.QRect(10, 40, 211, 31))
        self.lineEdit_year.setObjectName("lineEdit_year")
        self.lineEdit_title = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_title.setGeometry(QtCore.QRect(10, 100, 211, 31))
        self.lineEdit_title.setObjectName("lineEdit_title")
        self.lineEdit_duration = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_duration.setGeometry(QtCore.QRect(10, 160, 211, 31))
        self.lineEdit_duration.setObjectName("lineEdit_duration")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 762, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Пуск"))
        self.label.setText(_translate("MainWindow", "Год"))
        self.label_2.setText(_translate("MainWindow", "Название"))
        self.label_3.setText(_translate("MainWindow", "Длина"))
