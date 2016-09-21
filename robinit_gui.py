#! /usr/bin/env python2

'''
Frontend Aplication GUI
Latest Update - v1.0.1
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.0.1'

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.mainwindow import Ui_mainwindow
from gui.shows_mainwindow import Ui_shows_mainwindow
from gui.login import Ui_loginwindow
from libs.robinit_api import UserContent


class ShowsWindow(QMainWindow):
	def __init__(self, return_to):
		super(ShowsWindow, self).__init__()
		self.return_to=return_to

		# set up UI from QtDesigner
		self.ui = Ui_shows_mainwindow()
		self.ui.setupUi(self)
		self.ui.search_box.setFrame(False)
		self.ui.search_box.setFocus()

		self.ui.search_box.returnPressed.connect(self.search)
		self.ui.search_button.clicked.connect(self.search)

	def search(self):
		'''Searches for TV Show displaying results on page 1'''
		#hideAnimation = QtCore.QPropertyAnimation(self.ui.shows_label, "geometry")
		#hideAnimation.setDuration(10000)
		#hideAnimation.setStartValue(self.ui.shows_label.geometry()) # start at current position
		#finalGeometry = QtCore.QRect(100,100, 100,100)
		#hideAnimation.setEndValue(finalGeometry)
		#hideAnimation.start()

		self.ui.stackedWidget.setCurrentIndex(1)

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		# set up UI from QtDesigner
		self.ui = Ui_mainwindow()
		self.ui.setupUi(self)

		self.user_state = None

		self.move(200,200)
		self.show()
		self.setEnabled(False)

		self.loginwindow = LoginWindow(main_window=self)
		self.loginwindow.move(self.x()+200,self.y()+100) # position login window
		self.loginwindow.show()

		self.ui.shows_button.clicked.connect(self.display_shows_window)

	def display_shows_window(self):
		self.close()
		self.showswindow = ShowsWindow(return_to=self)
		self.showswindow.move(self.x(),self.y()) # position new window at the same position
		self.showswindow.show()

	def set_user_state(self, user_state):
		'''Sets user state to a given UserContent instance'''
		self.user_state=user_state


class LoginWindow(QMainWindow):
	def __init__(self, main_window):
		super(LoginWindow, self).__init__()
		self.main_window=main_window

		# set up UI from QtDesigner
		self.ui = Ui_loginwindow()
		self.ui.setupUi(self)

		self.ui.login_box.setFrame(False)
		self.ui.login_box.setFocus()

		# connect buttons
		self.ui.login_button.clicked.connect(self.login)
		self.ui.autologin_checkbox.stateChanged.connect(self.toogle_autologin)
		self.ui.login_box.returnPressed.connect(self.login)

		self.autologin = False

	def login(self):
		'''If a username is given it loads the user profile or creates a new one'''
		if self.ui.login_box.text() != "":
			user_state=UserContent(self.ui.login_box.text())
			self.main_window.set_user_state(user_state)
			self.main_window.setEnabled(True)
			self.close()
			self.destroy()

	def toogle_autologin(self):
		self.autologin = not self.autologin

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
