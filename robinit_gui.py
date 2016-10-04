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
Latest Update - v0.5
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.5'

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

# ----------------------------
#          Function
# ----------------------------

def save_config_file(content):
	'''Save given content to the CONFIG_FILE'''
	if type(content) == dict:
		fp = open(CONFIG_FILE, 'w')
		for key in content.keys():
			fp.write("%s %s\n" % (key, content[key]))
		fp.close()

def load_config_file():
	'''Load CONFIG_FILE to a dictionary, returning it'''
	content = {}
	try:
		fp = open(CONFIG_FILE, 'r')
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

		self.config = load_config_file() # get configs
		if 'default_user' in self.config.keys():
			self.set_user_state(UserContent(self.config['default_user']))
		else: # create login window
			self.setEnabled(False)
			self.loginwindow = LoginWindow(main_window=self, config=self.config)
			self.loginwindow.move(self.pos()+self.rect().center()-self.loginwindow.rect().center()) # position login window
			self.loginwindow.show()

		self.shows_window = ShowsMenu(return_to=self, user_state=self.user_state)
		self.settings = SettingsWindow(main_window=self, config=self.config)
		self.ui.shows_button.clicked.connect(partial(self.display_window, window=self.shows_window))
		self.ui.config_button.clicked.connect(self.display_settings)

	def display_window(self, window):
		'''Displays given window'''
		window.move(self.pos()+self.rect().center()-window.rect().center()) # position new window at the center position
		window.show()
		self.close()

	def display_settings(self):
		'''Separate function to display shows window due to it disabling the main menu while open'''
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
				self.config.update({'default_user' : self.ui.login_box.text().replace(' ', '_')})
				save_config_file(self.config)
			self.main_window.set_user_state(UserContent(self.ui.login_box.text().replace(' ', '_')))
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
		keys = self.config.keys()
		if not self.ui.kickass_checkbox.checkState(): self.config['kickass_allow'] = 'False' # default is True
		elif 'kickass_allow' in keys: del(self.config['kickass_allow'])
		if self.ui.rarbg_checkbox.checkState(): self.config['rarbg_allow'] = 'True' # default is False
		elif 'rarbg_allow' in keys: del(self.config['rarbg_allow'])
		if self.ui.piratebay_checkbox.checkState(): self.config['piratebay_allow'] = 'True' # default is False
		elif 'piratebay_allow' in keys: del(self.config['piratebay_allow'])

		if not self.ui.kickass_box.text() == "" : self.config['kickass'] = self.ui.kickass_box.text().replace(' ', '_') # default is empty
		elif 'kickass' in keys: del(self.config['kickass'])
		if not self.ui.rarbg_box.text() == "" : self.config['rarbg'] = self.ui.rarbg_box.text().replace(' ', '_') # default is empty
		elif 'rarbg' in keys: del(self.config['rarbg'])
		if not self.ui.piratebay_box.text() == "" : self.config['piratebay'] = self.ui.piratebay_box.text().replace(' ', '_') # default is empty
		elif 'piratebay' in keys: del(self.config['piratebay'])

		if not self.ui.ensub_checkbox.checkState(): self.config['sub_en'] = 'False' # default is True
		elif 'sub_en' in keys: del(self.config['sub_en'])
		if not self.ui.ptsub_checkbox.checkState(): self.config['sub_pt'] = 'False' # default is True
		elif 'sub_pt' in keys: del(self.config['sub_pt'])

		if self.ui.sd_button.isChecked(): self.config['def'] = 'sd'
		if self.ui.hd_button.isChecked(): self.config['def'] = 'hd'

		if not self.ui.storage_box.text() == "": self.config['storage_dir'] = self.ui.storage_box.text().replace(' ', '_') # default is empty
		elif 'storage_dir' in keys: del(self.config['storage_dir'])
		if not self.ui.user_box.text() == "": self.config['user_dir'] = self.ui.user_box.text().replace(' ', '_') # default is empty
		elif 'user_dir' in keys: del(self.config['user_dir'])
		if not self.ui.cache_box.text() == "": self.config['cache_dir'] = self.ui.cache_box.text().replace(' ', '_') # default is empty
		elif 'cache_dir' in keys: del(self.config['cache_dir'])

		if not self.ui.defaultuser_box.text() == "": self.config['default_user'] = self.ui.defaultuser_box.text().replace(' ', '_')
		elif 'default_user' in keys: del(self.config['default_user'])

		save_config_file(self.config)
		self.go_back()

	def configure(self):
		'''Sets the settings displayed according to given config dictionary'''
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


# ----------------
#		MAIN
# ----------------

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
