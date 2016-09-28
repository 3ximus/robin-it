#! /usr/bin/env python2

'''
Frontend Aplication GUI
Latest Update - v0.2
Created - 21.9.16
Copyright (C) 2016 - eximus
'''
__version__ = '0.2'

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor
from gui.mainwindow import Ui_mainwindow
from gui.shows_mainwindow import Ui_shows_mainwindow
from gui.login import Ui_loginwindow
from gui.settings import Ui_settings_window
from gui.show import Ui_show_window
from gui.show_banner_widget import Ui_show_banner_widget
from libs.robinit_api import UserContent
from libs.tvshow import search_for_show, Show
from libs.loading import progress_bar
from functools import partial
from threading import Thread
from cStringIO import StringIO
from PIL import Image, ImageFilter
import Queue
import urllib
import sys

BLUR_RADIOUS = 10
DARKNESS = 0.6

# ----------------------------
#       Thread Decorator
# ----------------------------
def threaded(function, daemon=False):
	'''Decorator to make a function threaded

		To acess wrapped funciton return value use .get()
	'''
	def wrapped_function(queue, *args, **kwargs):
		return_val = function(*args, **kwargs)
		queue.put(return_val)

	def wrap(*args, **kwargs):
		queue = Queue.Queue()

		thread = Thread(target=wrapped_function, args=(queue,)+args , kwargs=kwargs)
		thread.daemon=daemon
		thread.start()
		thread.result_queue=queue
		return queue
	return wrap

# ----------------------------
#          Function
# ----------------------------

@threaded
def download_image(signal, url, filters=False):
	'''Thread to download image, emits signal when complete'''
	data = urllib.urlopen(url).read()
	if filters: data = apply_filters(data)
	signal.emit(data)

def apply_filters(data):
	'''Function to apply filter to image'''
	data = StringIO(data)
	img = Image.open(data)
	img = img.point(lambda x: x*DARKNESS) # darken
	img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIOUS)) # blur
	tmp_data = StringIO()
	img.save(tmp_data, format='PNG')
	data = tmp_data.getvalue()
	tmp_data.close()
	return data

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

# ----------------------------
#         GUI Classes
# ----------------------------

class ShowWindow(QMainWindow):
	show_loaded = QtCore.pyqtSignal()
	background_loaded = QtCore.pyqtSignal(object)
	update_done = QtCore.pyqtSignal()

	def __init__(self, tvshow):
		super(ShowWindow, self).__init__()

		# set up UI from QtDesigner
		self.ui = Ui_show_window()
		self.ui.setupUi(self)

		self.background = None
		self.ui.showname_label.setText("> %s" % tvshow['seriesname'])
		self.ui.back_button.clicked.connect(self.close)
		self.ui.refresh_button.clicked.connect(self.update_show)
		self.ui.refresh_button_2.clicked.connect(self.update_show)
		self.ui.refresh_button.clicked.connect(self._update_status)
		self.ui.refresh_button_2.clicked.connect(self._update_status)
		self.show_loaded.connect(self.fill_info)
		self.update_done.connect(self.fill_updated_info)
		self.ui.statusbar.showMessage("Loading \"%s\" page..." % tvshow['seriesname'])
		self.load_show(tvshow['seriesname'])

	@threaded
	def load_show(self, name):
		'''Loads show from database'''
		self.tvshow = Show(name, header_only=True)
		self.show_loaded.emit()
		print "Show Loaded: %s\n" % name

	def fill_info(self):
		'''Fill in info after loaded, starting background download'''
		if self.tvshow.poster:
			self.ui.statusbar.showMessage("Loading Background...")
			self.background_loaded.connect(self.load_background)
			download_image(self.background_loaded, self.tvshow.poster, filters=True)
		self.ui.genre_label.setText('> genre - %s' % self.tvshow.genre)
		self.ui.network_label.setText('> network - %s' % self.tvshow.network)
		self.ui.airday_label.setText('> air day - %s : %s' % (self.tvshow.air_dayofweek, self.tvshow.air_time))
		self.ui.runtime_label.setText('> runtime - %s min' % self.tvshow.runtime)
		self.ui.status_label.setText('> status - %s' % self.tvshow.status)
		self.ui.imdb_label.setText('> <a href="%s"><span style=" text-decoration: underline; color:#03a662;">imdb</span></a> - %s' % (self.tvshow.imdb_id, self.tvshow.rating))
		self.ui.description_box.setText(self.tvshow.description)

	def load_background(self, data):
		'''Load window background from downloaded background image'''
		palette = QPalette()
		self.background = QPixmap()
		self.background.loadFromData(data)
		self.back_ratio = self.background.size().width()/float(self.background.size().height())
		self.background=self.background.scaled(QtCore.QSize(self.size().width(),self.size().width()/float(self.back_ratio)))
		palette.setBrush(QPalette.Background, QBrush(self.background))
		self.setPalette(palette)
		self.ui.statusbar.clearMessage()

	def resizeEvent(self, event):
		'''Called when resize is made'''
		if self.background:
			palette = QPalette()
			self.background=self.background.scaled(QtCore.QSize(self.size().width(),self.size().width()/float(self.back_ratio)))
			palette.setBrush(QPalette.Background, QBrush(self.background))
			self.setPalette(palette)

	@threaded
	def update_show(self, event):
		self.tvshow.update_info(override_cache='cache/')
		self.update_done.emit()

	def fill_updated_info(self):
		self.ui.statusbar.clearMessage()
		print self.tvshow.seasons[0].poster

	def _update_status(self, event):
		self.ui.statusbar.showMessage("Loading info...")

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

class ShowBanner(QWidget):
	banner_loaded = QtCore.pyqtSignal(object)

	def __init__(self, tvshow):
		super(ShowBanner, self).__init__()
		self.tvshow = tvshow

		self.ui = Ui_show_banner_widget()
		self.ui.setupUi(self)
		self.ui.name_label.setText('< %s >' % self.tvshow['seriesname'])

		self.ui.view_button.clicked.connect(self.view_show)
		self.ui.add_button.clicked.connect(self.add_show)

		if 'banner' in self.tvshow.keys():
			self.banner_loaded.connect(self.load_banner)
			self.download_banner("http://thetvdb.com/banners/" + self.tvshow['banner'])
		else:
			self.banner_loaded.emit("") # FIXME not working

	@threaded
	def download_banner(self, url): #FIXME there was some problem when using the download_image function (something about this class not having a signal with the signature banner_loaded signal(PyQt_PyObject))
		'''Thread to download banner, emits signal when complete'''
		data = urllib.urlopen(url).read()
		self.banner_loaded.emit(data)

	def load_banner(self, data):
		'''Loads the banner from downloaded data'''
		if data == "": # FIXME ridiculous atempt to force display of "no image available"
			return
		banner = QPixmap()
		banner.loadFromData(data)
		self.ui.banner.setPixmap(banner)

	def view_show(self):
		self.show_window = ShowWindow(self.tvshow)
		self.show_window.show()

	def add_show(self):
		pass

class ShowsMainWindow(QMainWindow):
	search_complete_signal = QtCore.pyqtSignal(object)

	def __init__(self, return_to, user_state):
		super(ShowsMainWindow, self).__init__()
		self.return_to=return_to
		self.user_state=user_state

		# set up UI from QtDesigner
		self.ui = Ui_shows_mainwindow()
		self.ui.setupUi(self)
		self.ui.search_box.setFocus()

		self.ui.search_box.returnPressed.connect(self.search)
		self.ui.search_box_2.returnPressed.connect(self.search)
		self.ui.search_button.clicked.connect(self.search)
		self.ui.search_button_2.clicked.connect(self.search)
		self.search_complete_signal.connect(self.display_results)

		self.ui.back_button_0.clicked.connect(self.go_back)
		self.ui.back_button_1.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_2.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_3.clicked.connect(partial(self.go_to, index=0))

		self.ui.myshows_button.clicked.connect(partial(self.go_to, index=2))
		self.ui.towatch_button.clicked.connect(partial(self.go_to, index=3))

		self.ui.filter_box.textChanged.connect(self.update_filter)
		self.ui.search_box.textChanged.connect(self.update_search)
		self.ui.search_box_2.textChanged.connect(self.update_search_2)

	def search(self):
		'''Searches for TV Show'''
		self.resultid=0
		self.ui.statusbar.showMessage("Searching %s..." % self.ui.search_box.text())
		self.ui.noresults_label.setParent(None)
		self._search_thread(self.ui.search_box.text()) # both input boxes are synced
		self.ui.stackedWidget.setCurrentIndex(1)
		self.ui.search_box_2.setFocus()

	@threaded
	def _search_thread(self, text):
		'''Wrapper for the search function to make it threaded'''
		results = search_for_show(text)
		self.search_complete_signal.emit(results)

	def display_results(self, results):
		'''Displays TV show results on stack widget page 1'''
		def _add_to_layout(widget, *args):
			'''Takes the widget to be added'''
			self.ui.results_layout.addWidget(widget)
			return

		def _status_update(results):
			self.resultid+=1
			p = 100*self.resultid/len(results)
			bar = progress_bar(p, show_percentage=True)
			self.ui.statusbar.showMessage(bar)
			if self.resultid == len(results): # clear status bar after completion
				self.ui.statusbar.clearMessage()

		for i in reversed(range(self.ui.results_layout.count())): # clear previous results
			self.ui.results_layout.itemAt(i).widget().setParent(None)
		if len(results) == 0: # no results found
			self.ui.results_layout.addWidget(self.ui.noresults_label)
		else:
			for r in results: # display new results
				banner = ShowBanner(r)
				banner.banner_loaded.connect(partial(_add_to_layout, widget=banner))
				banner.banner_loaded.connect(partial(_status_update, results=results))

	def go_back(self):
		self.close()
		self.return_to.move(self.x(),self.y())
		self.return_to.show()

	def go_to(self, index):
		self.ui.stackedWidget.setCurrentIndex(index)
		if index==0: self.ui.search_box.setFocus()

	def update_filter(self):
		'''Updates scroll box content according to content of filter_box'''
		print self.ui.filter_box.text()

	def update_search(self):
		self.ui.search_box_2.setText(self.ui.search_box.text())
# TODO ALSO REDISPLAY SEARCH RESULTS

	def update_search_2(self):
		self.ui.search_box.setText(self.ui.search_box_2.text())

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

		self.shows_window = ShowsMainWindow(return_to=self, user_state=self.user_state)
		self.settings = SettingsWindow(main_window=self, config=self.config)
		self.ui.shows_button.clicked.connect(partial(self.display_window, window=self.shows_window))
		self.ui.config_button.clicked.connect(self.display_settings)

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

	def closeEvent(self, event):
		self.deleteLater()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
