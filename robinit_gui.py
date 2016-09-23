#! /usr/bin/env python2

'''
Frontend Aplication GUI
Latest Update - v1.0.1
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.0.1'

import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.mainwindow import Ui_mainwindow
from gui.shows_mainwindow import Ui_shows_mainwindow
from gui.login import Ui_loginwindow
from gui.settings import Ui_settings_window
from gui.show import Ui_show_window
from libs.robinit_api import UserContent
from functools import partial

class ShowWindow(QMainWindow):
	def __init__(self, return_to):
		super(ShowWindow, self).__init__()
		self.return_to=return_to

		# set up UI from QtDesigner
		self.ui = Ui_show_window()
		self.ui.setupUi(self)

class SettingsWindow(QMainWindow):
	def __init__(self, main_window, config):
		super(SettingsWindow, self).__init__()
		self.main_window=main_window
		self.config=config

		# set up UI from QtDesigner
		self.ui = Ui_settings_window()
		self.ui.setupUi(self)

		self.ui.back_button.clicked.connect(self.go_back)
		self.ui.save_button.clicked.connect(self.save)
		self.configure()

	def go_back(self):
		self.main_window.show()
		self.main_window.setEnabled(True)
		self.close()

	def save(self):
		'''Saves configuration to a file, ignores if its set to default'''
		keys = self.config.keys()
		if not self.ui.kickass_checkbox.checkState(): self.config['kickass_allow'] = 'False' # default is True
		elif 'kickass_allow' in keys: del(self.config['kickass_allow'])
		if self.ui.rarbg_checkbox.checkState(): self.config['rarbg_allow'] = 'True' # default is False
		elif 'rarbg_allow' in keys: del(self.config['rarbg_allow'])
		if self.ui.piratebay_checkbox.checkState(): self.config['piratebay_allow'] = 'True' # default is False
		elif 'piratebay_allow' in keys: del(self.config['piratebay_allow'])

		if not self.ui.kickass_box.text() == "" : self.config['kickass'] = self.ui.kickass_box.text() # default is empty
		elif 'kickass' in keys: del(self.config['kickass'])
		if not self.ui.rarbg_box.text() == "" : self.config['rarbg'] = self.ui.rarbg_box.text() # default is empty
		elif 'rarbg' in keys: del(self.config['rarbg'])
		if not self.ui.piratebay_box.text() == "" : self.config['piratebay'] = self.ui.piratebay_box.text() # default is empty
		elif 'piratebay' in keys: del(self.config['piratebay'])

		if not self.ui.ensub_checkbox.checkState(): self.config['sub_en'] = 'False' # default is True
		elif 'sub_en' in keys: del(self.config['sub_en'])
		if not self.ui.ptsub_checkbox.checkState(): self.config['sub_pt'] = 'False' # default is True
		elif 'sub_pt' in keys: del(self.config['sub_pt'])

		if self.ui.sd_button.isChecked(): self.config['def'] = 'sd'
		if self.ui.hd_button.isChecked(): self.config['def'] = 'hd'

		if not self.ui.storage_box.text() == "": self.config['storage_dir'] = self.ui.storage_box.text() # default is empty
		elif 'storage_dir' in keys: del(self.config['storage_dir'])
		if not self.ui.user_box.text() == "": self.config['user_dir'] = self.ui.user_box.text() # default is empty
		elif 'user_dir' in keys: del(self.config['user_dir'])
		if not self.ui.cache_box.text() == "": self.config['cache_dir'] = self.ui.cache_box.text() # default is empty
		elif 'cache_dir' in keys: del(self.config['cache_dir'])

		if not self.ui.defaultuser_box.text() == "": self.config['default_user'] = self.ui.defaultuser_box.text()
		elif 'default_user' in keys: del(self.config['default_user'])

		save_config_file(self.config)
		self.go_back()

	def configure(self):
		keys = self.config.keys()
		if 'kickass_allow' in keys:
			self.ui.kickass_checkbox.setCheckState(True if self.config['kickass_allow'] == 'True' else False)
		if 'rarbg_allow' in keys:
			self.ui.rarbg_checkbox.setCheckState(True if self.config['rarbg_allow'] == 'True' else False)
		if 'piratebay_allow' in keys:
			self.ui.piratebay_checkbox.setCheckState(True if self.config['piratebay_allow'] == 'True' else False)

		if 'kickass' in keys:
			self.ui.kickass_box.setText(self.config['kickass'])
		if 'rarbg' in keys:
			self.ui.rarbg_box.setText(self.config['rarbg'])
		if 'piratebay' in keys:
			self.ui.piratebay_box.setText(self.config['piratebay'])

		if 'sub_en' in keys:
			self.ui.ensub_checkbox.setCheckState(True if self.config['sub_en'] == 'True' else False)
		if 'sub_pt' in keys:
			self.ui.ptsub_checkbox.setCheckState(True if self.config['sub_pt'] == 'True' else False)

		if 'def' in keys:
			if self.config['def'] == 'sd':
				self.ui.sd_button.setChecked(True)
			elif self.config['def'] == 'hd':
				self.ui.hd_button.setChecked(True)

		if 'storage_dir' in keys:
			self.ui.storage_box.setText(self.config['storage_dir'])
		if 'user_dir' in keys:
			self.ui.user_box.setText(self.config['user_dir'])
		if 'cache_dir' in keys:
			self.ui.cache_box.setText(self.config['cache_dir'])
		if 'default_user' in keys:
			self.ui.defaultuser_box.setText(self.config['default_user'])

class ShowsMainWindow(QMainWindow):
	def __init__(self, return_to):
		super(ShowsMainWindow, self).__init__()
		self.return_to=return_to

		# set up UI from QtDesigner
		self.ui = Ui_shows_mainwindow()
		self.ui.setupUi(self)
		self.ui.search_box.setFocus()

		self.ui.search_box.returnPressed.connect(self.search)
		self.ui.search_button.clicked.connect(self.search)

		self.ui.back_button_0.clicked.connect(self.go_back)
		self.ui.back_button_1.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_2.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_3.clicked.connect(partial(self.go_to, index=0))

		self.ui.myshows_button.clicked.connect(partial(self.go_to, index=2))
		self.ui.towatch_button.clicked.connect(partial(self.go_to, index=3))

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

class LoginWindow(QMainWindow):
	def __init__(self, main_window, config):
		super(LoginWindow, self).__init__()
		self.main_window=main_window
		self.config=config

		# set up UI from QtDesigner
		self.ui = Ui_loginwindow()
		self.ui.setupUi(self)

		self.ui.login_box.setFocus()

		# connect buttons
		self.ui.login_button.clicked.connect(self.login)
		self.ui.autologin_checkbox.stateChanged.connect(self.toogle_autologin)
		self.ui.login_box.returnPressed.connect(self.login)

		self.autologin = False

	def login(self):
		'''If a username is given it loads the user profile or creates a new one'''
		if self.ui.login_box.text() != "":
			if self.autologin:
				self.config.update({'default_user' : self.ui.login_box.text()})
				save_config_file(self.config)
			self.main_window.set_user_state(UserContent(self.ui.login_box.text()))
			self.main_window.setEnabled(True)
			self.close()
			self.destroy()

	def toogle_autologin(self):
		self.autologin = not self.autologin

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		# set up UI from QtDesigner
		self.ui = Ui_mainwindow()
		self.ui.setupUi(self)

		# init window at center
		self.move(QApplication.desktop().screen().rect().center()-self.rect().center())
		self.show()

		self.config = load_config_file() # get configs
		if 'default_user' in self.config.keys():
			self.set_user_state(UserContent(self.config['default_user']))
		else: # create login window
			self.setEnabled(False)
			self.loginwindow = LoginWindow(main_window=self, config=self.config)
			self.loginwindow.move(self.pos()+self.rect().center()-self.loginwindow.rect().center()) # position login window
			self.loginwindow.show()

		self.ui.shows_button.clicked.connect(partial(self.display_window, window=ShowsMainWindow(return_to=self)))
		self.ui.config_button.clicked.connect(self.display_settings)
		self.settings = SettingsWindow(main_window=self, config=self.config)

		# User
		self.user_state = None

	def display_window(self, window):
		window.move(self.pos()+self.rect().center()-window.rect().center()) # position new window at the center position
		window.show()
		self.close()

	def display_settings(self):
		self.settings.move(self.pos()+self.rect().center()-self.settings.rect().center()) # position new window at the center position
		self.settings.show()
		self.setEnabled(False)

	def set_user_state(self, user_state):
		'''Sets user state to a given UserContent instance'''
		self.user_state=user_state
		self.ui.user_label.setText('<%s>' % self.user_state.username)

def save_config_file(content):
	if type(content) == dict:
		fp = open('robinit.conf', 'w')
		for key in content.keys():
			fp.write("%s %s\n" % (key, content[key]))
		fp.close()

def load_config_file():
	content = {}
	try:
		fp = open('robinit.conf', 'r')
		for n, line in enumerate(fp):
			if line[0] == '#': continue
			line = [s.strip('\n') for s in line.split(' ')]
			if len(line) != 2 or line[1] == "":
				raise ValueError("\033[0;31mError in line %d : \" %s \" in robinit.conf\033[0m" % (n, ' '.join(line)))
			key, value = line
			content.update({key : value})
		fp.close()
	except IOError: pass
	return content

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
