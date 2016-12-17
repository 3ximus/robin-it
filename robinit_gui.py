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
Notes: Uses a global config class through the settings file
Latest Update - v1.0
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '1.0'

# PYQT5 IMPORTS
from PyQt5.QtWidgets import QApplication, QMainWindow

# IMPORT FORMS
from gui.resources.mainwindow import Ui_mainwindow
from gui.resources.login import Ui_loginwindow
from gui.resources.settings import Ui_settings_window

# GUI CLASSES
from gui.show_menu import ShowsMenu
from libs.config import Config

# LIBS IMPORT
from libs.robinit_api import UserContent
import settings

# TOOLS
from functools import partial
import sys

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
		self.shows_window = None
		self.settings = None

		settings.config = Config(settings._CONFIG_FILE, default_config=settings._DEFAULTS)
		if settings.config.has_property('default_user'):
			self.set_user_state(UserContent(settings.config['default_user'],
					user_dir=settings.config['user_dir'] if settings.config.has_property('user_dir') else None,
					cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None,
					storage_dir=settings.config['storage_dir'] if settings.config.has_property('storage_dir') else None,
					apikey=settings._TVDB_API_KEY))
		else: # create login window, this will use the function self.set_user_state to set the user_state
			self.setEnabled(False)
			self.loginwindow = LoginWindow(main_window=self)
			self.loginwindow.move(self.pos()+self.rect().center()-self.loginwindow.rect().center()) # position login window
			self.loginwindow.show()

		print "Loaded user \"%s\"" % self.user_state.username
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
		self.settings = SettingsWindow(main_window=self)
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
		pass
		# TODO improve this
		#self.deleteLater()


class LoginWindow(QMainWindow):
	'''Class for logging in the user

	Parameters:
		main_window -- window to return after login (usually the main menu window)
		config -- config dictionary loaded from CONFIG_FILE usually

		Expect user to input username, if not given it creates a new one
		Autologin checkbox saves the user to the config dictionary given avoiding this window when app launched
	'''
	def __init__(self, main_window):
		super(LoginWindow, self).__init__()
		self.main_window=main_window

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
			username = self.ui.login_box.text().replace(' ', '_')
			if self.autologin:
				settings.config.add_property('default_user', username)
				settings.config.save()
			self.main_window.set_user_state(
				UserContent(username,
						user_dir=settings.config['user_dir'] if settings.config.has_property('user_dir') else None,
						cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None,
						storage_dir=settings.config['storage_dir'] if settings.config.has_property('storage_dir') else None,
						apikey=settings._TVDB_API_KEY))
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
	def __init__(self, main_window):
		super(SettingsWindow, self).__init__()
		self.main_window=main_window

		# set up UI from QtDesigner
		self.ui = Ui_settings_window()
		self.ui.setupUi(self)

		self.ui.back_button.clicked.connect(self.go_back)
		self.ui.save_button.clicked.connect(self.save)

		# update slider and text 0 identifies the slider and 1 identifies the text
		self.ui.update_interval_slider.sliderMoved.connect(partial(self.update_show_interval, 0))
		self.ui.update_interval_value.textChanged.connect(partial(self.update_show_interval, 1))

		self.configure()

	def go_back(self):
		'''Closes window and reenables to main_menu'''
		self.close()

	def closeEvent(self, event):
		self.main_window.show()
		self.main_window.setEnabled(True)

	def update_show_interval(self, entity):
		'''Updates the slider or the text based on given entity (0 -> means slider called, 1 -> means text_input called)'''
		if entity == 0:
			self.ui.update_interval_value.setText(str(self.ui.update_interval_slider.sliderPosition()))
		else:
			try:
				val = int(self.ui.update_interval_value.text())
				val = 1 if val < 1 else (settings._MAX_UPDATE_SHOW_INTERVAL if val > settings._MAX_UPDATE_SHOW_INTERVAL else val) # clamp the value
				self.ui.update_interval_slider.setSliderPosition(val)
			except ValueError: pass
			finally: self.ui.update_interval_value.setText(str(self.ui.update_interval_slider.sliderPosition()))

	def save(self):
		'''Saves configuration to a file, ignores or deletes a settinf from config dict if its set to default'''

		settings.config.add_property('piratebay_allow', self.ui.piratebay_checkbox.isChecked(), 'torrents')
		settings.config.add_property('piratebay', self.ui.piratebay_box.text().replace(' ', '_'), 'torrents')
		settings.config.add_property('kickass_allow', self.ui.kickass_checkbox.isChecked(), 'torrents')
		settings.config.add_property('kickass', self.ui.kickass_box.text().replace(' ', '_'), 'torrents')
		settings.config.add_property('rarbg_allow', self.ui.rarbg_checkbox.isChecked(), 'torrents')
		settings.config.add_property('rarbg', self.ui.rarbg_box.text().replace(' ', '_'), 'torrents')

		settings.config.add_property('sub_en', self.ui.ensub_checkbox.isChecked(), 'subtitles')
		settings.config.add_property('sub_pt', self.ui.ensub_checkbox.isChecked(), 'subtitles')

		if self.ui.sd_button.isChecked(): settings.config.add_property('definition', 'sd')
		if self.ui.hd_button.isChecked(): settings.config.add_property('definition', 'hd')

		settings.config.add_property('storage_dir',self.ui.storage_box.text().replace(' ', '_'), 'directories')
		settings.config.add_property('user_dir', self.ui.user_box.text().replace(' ', '_'), 'directories')
		settings.config.add_property('cache_dir', self.ui.cache_box.text().replace(' ', '_'), 'directories')
		self.main_window.user_state.set_storage_dir(settings.config['storage_dir'] if settings.config['storage_dir'] != '' else None)
		self.main_window.user_state.set_user_dir(settings.config['user_dir'] if settings.config['user_dir'] != '' else None)
		self.main_window.user_state.set_cache_dir(settings.config['cache_dir'] if settings.config['cache_dir'] != '' else None)
		self.main_window.user_state.save_state()

		settings.config.add_property('update_show_interval', self.ui.update_interval_slider.sliderPosition())

		settings.config.add_property('default_user',self.ui.defaultuser_box.text().replace(' ', '_'))

		settings.config.save()
		self.go_back()

	def configure(self):
		'''Sets the settings displayed according to given config dictionary'''
		if settings.config.has_property('piratebay_allow'):
			self.ui.piratebay_checkbox.setChecked(settings.config['piratebay_allow'])
		if settings.config.has_property('kickass_allow'):
			self.ui.kickass_checkbox.setChecked(settings.config['kickass_allow'])
		if settings.config.has_property('rarbg_allow'):
			self.ui.rarbg_checkbox.setChecked(settings.config['rarbg_allow'])

		if settings.config.has_property('piratebay'):
			self.ui.piratebay_box.setText(str(settings.config['piratebay'] if settings.config['piratebay'] != settings._DEFAULTS['torrents']['piratebay'] else ''))
		if settings.config.has_property('kickass'):
			self.ui.kickass_box.setText(str(settings.config['kickass'] if settings.config['kickass'] != settings._DEFAULTS['torrents']['kickass'] else ''))
		if settings.config.has_property('rarbg'):
			self.ui.rarbg_box.setText(str(settings.config['rarbg'] if settings.config['rarbg'] != settings._DEFAULTS['torrents']['rarbg'] else ''))

		# set placeholder texts for this (given by source update)
		self.ui.piratebay_box.setPlaceholderText(str(settings._DEFAULTS['torrents']['piratebay']))
		self.ui.kickass_box.setPlaceholderText(str(settings._DEFAULTS['torrents']['kickass']))
		self.ui.rarbg_box.setPlaceholderText(str(settings._DEFAULTS['torrents']['rarbg']))

		if settings.config.has_property('sub_en'):
			self.ui.ensub_checkbox.setChecked(settings.config['sub_en'])
		if settings.config.has_property('sub_pt'):
			self.ui.ptsub_checkbox.setChecked(settings.config['sub_pt'])

		if settings.config.has_property('definition'):
			if settings.config['definition'] == 'sd':
				self.ui.sd_button.setChecked(True)
			elif settings.config['definition'] == 'hd':
				self.ui.hd_button.setChecked(True)

		if settings.config.has_property('storage_dir'):
			self.ui.storage_box.setText(str(settings.config['storage_dir'] if settings.config['storage_dir'] != settings._DEFAULTS['directories']['storage_dir'] else ''))
		if settings.config.has_property('user_dir'):
			self.ui.user_box.setText(str(settings.config['user_dir'] if settings.config['user_dir'] != settings._DEFAULTS['directories']['user_dir'] else ''))
		if settings.config.has_property('cache_dir'):
			self.ui.cache_box.setText(str(settings.config['cache_dir'] if settings.config['cache_dir'] != settings._DEFAULTS['directories']['cache_dir'] else ''))

		if settings.config.has_property('update_show_interval'):
			self.ui.update_interval_slider.setSliderPosition(settings.config['update_show_interval'])
			self.update_show_interval(0)

		if settings.config.has_property('default_user'):
			self.ui.defaultuser_box.setText(str(settings.config['default_user']))

# ----------------
#		MAIN
# ----------------

if __name__ == "__main__":
	settings.init()
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
