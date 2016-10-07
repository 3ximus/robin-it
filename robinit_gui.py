#! /usr/bin/python2.7
#Robin It - Track tvshows and download its torrents
#Copyright (C) 2016  Fabio Almeida
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
Frontend Aplication GUI
Latest Update - v0.6
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.6'

# PYQT5 IMPORTS
from PyQt5.QtWidgets import QApplication, QMainWindow

# IMPORT FORMS
from gui.resources.mainwindow import Ui_mainwindow
from gui.resources.login import Ui_loginwindow
from gui.resources.settings import Ui_settings_window

# GUI CLASSES
from gui.show_menu import *
from gui.show_window import *

# LIBS IMPORT
from libs.robinit_api import UserContent

# TOOLS
from functools import partial
import sys

# ----------------------------
#         Globals
# ----------------------------

CONFIG_FILE = 'robinit.conf'
DEFAULTS =  {'kickass_allow':True,
				'rarbg_allow':False,
				'pirateaby_allow':False,
				'kickass':'',
				'rarbg':'',
				'piratebay':'',
				'sub_en':True,
				'sub_pt':True,
				'definition':'hd',
				'storage_dir':'',
				'user_dir':'',
				'cache_dir':'',
				'default_user':''}

# ----------------------------
#         GUI Classes
# ----------------------------

class MainWindow(QMainWindow):
	'''Main window class containing the main menu

		This class launches other parts of the program like the Shows and Movies, through its menu
		This class when created lods the CONFIG_FILE if available, if the default user is set its saved profile is loaded
			otherwise a LoginWindow is presented so the user can select a profile or create a new one
	'''
	def __init__(self):
		super(MainWindow, self).__init__()

		# set up UI from QtDesigner
		self.ui = Ui_mainwindow()
		self.ui.setupUi(self)

		# init window at center
		self.move(QApplication.desktop().screen().rect().center()-self.rect().center())
		self.show()

		# User
		self.user_state = None

		self.config = Config(CONFIG_FILE, default_config=DEFAULTS)
		if self.config.has_property('default_user'):
			self.set_user_state(UserContent(self.config.default_user,
					user_dir=self.config.user_dir if self.config.has_property('user_dir') else None,
					cache_dir=self.config.cache_dir if self.config.has_property('cache_dir') else None,
					storage_dir=self.config.storage_dir if self.config.has_property('storage_dir') else None))
		else: # create login window, this will use the function self.set_user_state to set the user_state
			self.setEnabled(False)
			self.loginwindow = LoginWindow(main_window=self, config=self.config)
			self.loginwindow.move(self.pos()+self.rect().center()-self.loginwindow.rect().center()) # position login window
			self.loginwindow.show()

		self.ui.shows_button.clicked.connect(self.display_shows)
		self.ui.config_button.clicked.connect(self.display_settings)

	def display_shows(self):
		'''Displays Shows Menu'''
		self.shows_window = ShowsMenu(return_to=self, user_state=self.user_state)
		self.shows_window.move(self.pos()+self.rect().center()-self.shows_window.rect().center()) # position new window at the center position
		self.shows_window.show()
		self.close()

	def display_settings(self):
		'''Display Settings Menu'''
		self.settings = SettingsWindow(main_window=self, config=self.config)
		self.settings.move(self.pos()+self.rect().center()-self.settings.rect().center()) # position new window at the center position
		self.settings.show()
		self.setEnabled(False)

	def set_user_state(self, user_state):
		'''Sets user state to a given UserContent instance
			This is called either at construction time if a default user is set in the CONFIG_FILE or
				by the login window when selecting a profile
		'''
		self.user_state=user_state
		self.ui.user_label.setText('<%s>' % self.user_state.username)

	def closeEvent(self, event):
		'''This is here because it stops segmentation fault when exiting, but stops the
			possibily of returning to the main menu after other menus are loaded and
			this one is closed

			NOTE: something here needs tweaking to prevent fatal crash
			when other menus try to return to this window
		'''
		self.deleteLater()


class LoginWindow(QMainWindow):
	'''Class for logging in the user

	Parameters:
		main_window -- window to return after login (usually the main menu window)
		config -- config dictionary loaded from CONFIG_FILE usually

		Expect user to input username, if not given it creates a new one
		Autologin checkbox saves the user to the config dictionary given avoiding this window when app launched
	'''
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
		'''Triggered by a returnPressed on login_box or clicked on login_button signals

			Logs the user in, effectivly loading its profile if available, otherwise it creates a new one
			If the autologin checkbox is checked it will save this user to the config file
		'''
		if self.ui.login_box.text() != "":
			if self.autologin:
				self.config.add_property('default_user', self.ui.login_box.text().replace(' ', '_'))
				self.config.save()
			self.main_window.set_user_state(
				UserContent(self.ui.login_box.text().replace(' ', '_'),
						user_dir=self.config.user_dir if self.config.has_property('user_dir') else None,
						cache_dir=self.config.cache_dir if self.config.has_property('cache_dir') else None,
						storage_dir=self.config.storage_dir if self.config.has_property('storage_dir') else None))
			self.main_window.setEnabled(True)
			self.close()
			self.destroy()

	def toogle_autologin(self):
		'''Triggered by self.ui.autologin_checkbox.stateChanged signal.
			Toogles autologin variable when self.ui.autologin_checkbox state is changed
		'''
		self.autologin = not self.autologin

class SettingsWindow(QMainWindow):
	'''Settings window class

	Parameters:
		main_window -- window to return after login (usually the main menu window)
		config -- config dictionary loaded from CONFIG_FILE usually

		This class contains multiple settings that are save on the CONFIG_FILE when the save_button is pressed
	'''
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
		'''Closes window and reenables to main_menu'''
		self.main_window.show()
		self.main_window.setEnabled(True)
		self.close()

	def save(self):
		'''Saves configuration to a file, ignores or deletes a settinf from config dict if its set to default'''

		self.config.add_property('kickass_allow', self.ui.kickass_checkbox.isChecked())
		self.config.add_property('rarbg_allow', self.ui.rarbg_checkbox.isChecked())
		self.config.add_property('piratebay_allow', self.ui.piratebay_checkbox.isChecked())
		self.config.add_property('kickass', self.ui.kickass_box.text().replace(' ', '_'))
		self.config.add_property('rarbg', self.ui.rarbg_box.text().replace(' ', '_'))
		self.config.add_property('piratebay', self.ui.piratebay_box.text().replace(' ', '_'))

		self.config.add_property('sub_en', self.ui.ensub_checkbox.isChecked())
		self.config.add_property('sub_pt', self.ui.ensub_checkbox.isChecked())

		if self.ui.sd_button.isChecked(): self.config.add_property('definition', 'sd')
		if self.ui.hd_button.isChecked(): self.config.add_property('definition', 'hd')

		self.config.add_property('storage_dir',self.ui.storage_box.text().replace(' ', '_'))
		self.config.add_property('user_dir', self.ui.user_box.text().replace(' ', '_'))
		self.config.add_property('cache_dir', self.ui.cache_box.text().replace(' ', '_'))

		self.config.add_property('default_user',self.ui.defaultuser_box.text().replace(' ', '_'))

		self.config.save()
		self.go_back()

	def configure(self):
		'''Sets the settings displayed according to given config dictionary'''
		if self.config.has_property('kickass_allow'):
			self.ui.kickass_checkbox.setChecked(self.config.kickass_allow)
		if self.config.has_property('rarbg_allow'):
			self.ui.rarbg_checkbox.setChecked(self.config.rarbg_allow)
		if self.config.has_property('piratebay_allow'):
			self.ui.piratebay_checkbox.setChecked(self.config.piratebay_allow)

		if self.config.has_property('kickass'):
			self.ui.kickass_box.setText(self.config.kickass)
		if self.config.has_property('rarbg'):
			self.ui.rarbg_box.setText(self.config.rarbg)
		if self.config.has_property('piratebay'):
			self.ui.piratebay_box.setText(self.config.piratebay)

		if self.config.has_property('sub_en'):
			self.ui.ensub_checkbox.setChecked(self.config.sub_en)
		if self.config.has_property('sub_pt'):
			self.ui.ptsub_checkbox.setChecked(self.config.sub_pt)

		if self.config.has_property('definition'):
			if self.config.definition == 'sd':
				self.ui.sd_button.setChecked(True)
			elif self.config.definition == 'hd':
				self.ui.hd_button.setChecked(True)

		if self.config.has_property('storage_dir'):
			self.ui.storage_box.setText(self.config.storage_dir)
		if self.config.has_property('user_dir'):
			self.ui.user_box.setText(self.config.user_dir)
		if self.config.has_property('cache_dir'):
			self.ui.cache_box.setText(self.config.cache_dir)
		if self.config.has_property('default_user'):
			self.ui.defaultuser_box.setText(self.config.default_user)

# ----------------
#		MAIN
# ----------------

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
