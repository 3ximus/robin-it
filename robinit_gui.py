#! /usr/bin/env python2

'''
Frontend Aplication GUI
Latest Update - v1.0.1
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.0.1'

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.mainwindow import Ui_mainWindow

app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_mainWindow()
ui.setupUi(window)
window.show()
sys.exit(app.exec_())

