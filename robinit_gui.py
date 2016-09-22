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
from gui.settings import Ui_settings_window
from libs.robinit_api import UserContent


class SettingsWindow(QMainWindow):
	def __init__(self, return_to):
		super(SettingsWindow, self).__init__()
		self.return_to=return_to

		# set up UI from QtDesigner
		self.ui = Ui_settings_window()
		self.ui.setupUi(self)
		self.ui.storage_box.setFrame(False)

		self.ui.back_button.clicked.connect(self.go_back)

	def go_back(self):
		self.close()
		self.return_to.move(self.x(),self.y())
		self.return_to.show()

class ShowsWindow(QMainWindow):
	def __init__(self, return_to):
		super(ShowsWindow, self).__init__()
		self.return_to=return_to

		# set up UI from QtDesigner
		self.ui = Ui_shows_mainwindow()
		self.ui.setupUi(self)
		self.ui.filter_box.setFrame(False)
		self.ui.search_box.setFrame(False)
		self.ui.search_box.setFocus()

		self.ui.search_box.returnPressed.connect(self.search)
		self.ui.search_button.clicked.connect(self.search)

		self.ui.back_button_0.clicked.connect(self.go_back)
		self.ui.back_button_1.clicked.connect(lambda: self.go_to(0))
		self.ui.back_button_2.clicked.connect(lambda: self.go_to(0))

		self.ui.filter_box.textChanged.connect(self.update_filter)
		self.ui.search_box.textChanged.connect(self.update_search)

	def search(self):
		'''Searches for TV Show displaying results on page 1'''
		self.ui.stackedWidget.setCurrentIndex(1)

	def go_back(self):
		self.close()
		self.return_to.move(self.x(),self.y())
		self.return_to.show()

	def go_to(self, index):
		self.ui.stackedWidget.setCurrentIndex(index)

	def update_filter(self):
		'''Updates scroll box content according to content of filter_box'''
		print self.ui.filter_box.text()

	def update_search(self):
		'''Display suggested shows according to typed content'''
		pass

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

		self.ui.shows_button.clicked.connect(lambda: self.display_window(ShowsWindow(return_to=self)))
		#self.ui.config_button.clicked.connect(lambda: self.display_window(SettingsWindow(return_to=self)))
		self.ui.config_button.clicked.connect(self.disp_sett) # XXX PLACEHOLDER

	def display_window(self, window): # FIXME not working
		window.move(self.x(),self.y()) # position new window at the same position
		window.show()
		self.close()

	def disp_sett(self): # XXX PLACEHOLDER
		window2 = SettingsWindow(return_to=self)
		window2.move(self.x(),self.y()) # position new window at the same position
		window2.show()
		self.close()

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
