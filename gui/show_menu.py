
'''
GUI for the TV Shows main menu
Latest Update - v0.4
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.4'

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor

# IMPORT FORMS
from gui.resources.shows_menu import Ui_shows_menu
from gui.resources.show_banner_widget import Ui_show_banner_widget

# LIBS IMPORT
from gui_func import clickable, begin_hover, end_hover 
from show_window import ShowWindow
from libs.tvshow import search_for_show
from libs.thread_decorator import threaded
from libs.loading import progress_bar

# TOOLS
from time import sleep
from functools import partial
import urllib

# FIXED VALUES

MAIN_COLOR =  "#03a662"
RED_COLOR =  "#bf273d"
TVDB_BANNER_PREFIX = "http://thetvdb.com/banners/"

class ShowsMenu(QMainWindow):
	'''Works with stacked pages

	Parameters:
		return_to -- window to show when the back_button is pressed
		user_state -- UserContent class instance containing user info

	Index:
		0 - Main Page contains search box and updates
		1 - Results from search box
		2 - List of followed shows
		3 - List of shows to watch

		Emits the search_complete signal when it gathers the search results for given keywords
		Emits all_banners_loaded as an internal signal for loading the remaining bannerless
			results (do not use outside this class)
	'''
	search_complete = QtCore.pyqtSignal(object)
	all_banners_loaded = QtCore.pyqtSignal()

	def __init__(self, return_to, user_state):
		super(ShowsMenu, self).__init__()
		self.return_to=return_to
		self.user_state=user_state

		# set up UI from QtDesigner
		self.ui = Ui_shows_menu()
		self.ui.setupUi(self)
		self.ui.search_box.setFocus()

		self.ui.search_box.returnPressed.connect(self.search)
		self.ui.search_box_2.returnPressed.connect(self.search)
		self.ui.search_button.clicked.connect(self.search)
		self.ui.search_button_2.clicked.connect(self.search)
		self.search_complete.connect(self.display_results)

		self.ui.back_button_0.clicked.connect(self.go_back)
		self.ui.back_button_1.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_2.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_3.clicked.connect(partial(self.go_to, index=0))

		self.ui.myshows_button.clicked.connect(self.load_my_shows)
		self.ui.towatch_button.clicked.connect(partial(self.go_to, index=3))

		self.ui.filter_box.textChanged.connect(self.update_filter)
		self.ui.search_box.textChanged.connect(self.update_search)
		self.ui.search_box_2.textChanged.connect(self.update_search_2)

	def search(self):
		'''Searches for TV Show by a given keyword in the search box
			Displays results on page 1
		'''
		self.loaded_results=0
		self.ui.statusbar.showMessage("Searching for %s..." % self.ui.search_box.text())
		self.ui.noresults_label.setParent(None)
		self._search_thread(self.ui.search_box.text()) # both input boxes are synced
		self.ui.stackedWidget.setCurrentIndex(1)
		self.ui.search_box_2.setFocus()

	@threaded
	def _search_thread(self, text):
		'''Searches for TV shows by given keywords
			Emits self.search_complete when finished
		'''
		results = search_for_show(text)
		self.search_complete.emit(results)

	def display_results(self, results):
		'''Triggered by the self.search_complete signal. Displays TV show results on stack widget page 1

			Cleans the layout and adds show widgets when they finish loading the respective banners.
			Shows without banners are left pending until self.all_banners_loaded signal
			is triggered, displaying the remaining results.
			This is done in order to only display bannerless shows at the end
		'''
		def _add_to_layout(widget, *args):
			'''Takes the widget to be added'''
			self.ui.results_layout.addWidget(widget)
			return

		def _status_update(results):
			'''Updates Status bar loading message with progress_bar'''
			self.loaded_results+=1
			p = 100*self.loaded_results/len(results)
			bar = progress_bar(p, show_percentage=True)
			self.ui.statusbar.showMessage(bar)
			if self.loaded_results == len(results): # clear status bar after completion
				self.ui.statusbar.clearMessage()

		@threaded
		def _wait_for_loading(results, pending_add):
			'''This thread will simply wait until all shows with banners are loaded
				Emits self.all_banners_loaded when finished
			'''
			while True:
				if self.loaded_results == len(results)-len(pending_add):
					self.all_banners_loaded.emit()
					return
				sleep(1)

		def _display_pending(pending):
			'''Triggered by self.all_banners_loaded signal. Display shows without banner'''
			for p in pending: # add the shows without banner at the end
				self.ui.results_layout.addWidget(ShowWidget(self, p))
				_status_update(results=results)

		for i in reversed(range(self.ui.results_layout.count())): # clear previous results
			self.ui.results_layout.itemAt(i).widget().setParent(None)
		if len(results) == 0: # no results found
			self.ui.results_layout.addWidget(self.ui.noresults_label)
		else:
			pending_add = []
			try: self.all_banners_loaded.disconnect() # disconnect signals in order to not connect duplicates
			except TypeError: pass
			self.all_banners_loaded.connect(partial(_display_pending, pending=pending_add))
			for r in results: # display new results
				banner = ShowWidget(self, r)
				if 'banner' not in r: # shows without banners added to pending add
					pending_add.append(r)
				else:
					banner.banner_loaded.connect(partial(_add_to_layout, widget=banner))
					banner.banner_loaded.connect(partial(_status_update, results=results))

			_wait_for_loading(results, pending_add) # add bannerless when all other shows are loaded

	def go_back(self):
		'''Closes this window and opens the Main Menu'''
		self.close()
		self.return_to.move(self.x(),self.y())
		self.return_to.show()

	def go_to(self, index):
		'''Got to one of the stacked pages given by index'''
		self.ui.stackedWidget.setCurrentIndex(index)
		if index==0: self.ui.search_box.setFocus()

	def load_my_shows(self):
		'''Load shows and got to page 2'''
		self.ui.stackedWidget.setCurrentIndex(2)
		self.ui.showfilter_box.setFocus()
		for i in reversed(range(self.ui.myshows_layout.count())): # clear previous results
			self.ui.myshows_layout.itemAt(i).widget().setParent(None)
		for show in self.user_state.shows.values():
			self.ui.myshows_layout.addWidget(ShowWidget(self, show))

	def update_filter(self):
		'''Updates the news updates content according to content of filter_box'''
		print self.ui.filter_box.text()

	def update_search(self):
		'''Maintains search boxes from both stack pages in sync'''
		self.ui.search_box_2.setText(self.ui.search_box.text())

	def update_search_2(self):
		'''Maintains search boxes from both stack pages in sync'''
		self.ui.search_box.setText(self.ui.search_box_2.text())


class ShowWidget(QWidget):
	'''Small banner to identify a show

	Parameters:
		tvshow -- search result to load the banner from or a Show instance

		The whole widget is clickable displaying a Show Window with the tvshow info
		Has an add button to add the show to the followed shows
		Emits banner_loaded signal when the banner image is loaded

		Used in search results
	'''
	banner_loaded = QtCore.pyqtSignal(object)

	def __init__(self, mainwindow, tvshow):
		super(ShowWidget, self).__init__()
		self.tvshow = tvshow
		self.main_window = mainwindow

		self.ui = Ui_show_banner_widget()
		self.ui.setupUi(self)
		
		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		self.ui.name_label.setText('< %s >' % name)
		clickable(self).connect(self.view_show)

		self.ui.add_button.clicked.connect(self.add_show)
		if self.main_window.user_state.is_tracked(name):
			self.make_del_button()

		if type(self.tvshow) == dict:
    			if 'banner' in self.tvshow.keys():
					self.banner_loaded.connect(self.load_banner)
					self.download_banner(TVDB_BANNER_PREFIX + self.tvshow['banner'])
		else:
			self.banner_loaded.connect(self.load_banner)
			self.download_banner(self.tvshow.banner)

	@threaded
	def download_banner(self, url):
		'''Thread to download banner, emits self.banner_loaded signal when complete'''
		data = urllib.urlopen(url).read()
		self.banner_loaded.emit(data)

	def load_banner(self, data):
		'''Triggered by self.banner_loaded signal. Loads the banner from downloaded data'''
		banner = QPixmap()
		banner.loadFromData(data)
		self.ui.banner.setPixmap(banner)

	def view_show(self):
		'''Triggered clicking on the widget. Displays Show Window'''
		self.show_window = ShowWindow(self.main_window, self.tvshow)
		self.show_window.show()

	def add_show(self):
		'''Triggered by clicking on self.ui.add_button. Adds show to be tracked'''
		self.main_window.user_state.add_show(self.tvshow['seriesname'])
		self.main_window.user_state.save_state()
		print "Added: " + self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		self.make_del_button()

	def make_del_button(self):
		'''Transforms the add button into a delete button'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("-del")
		self.ui.add_button.setStyleSheet("background-color: " + RED_COLOR)
		self.ui.add_button.clicked.connect(self.delete_show)

	def delete_show(self):
		'''Triggered by clicking on the add button when this show is added
		
			Stops show from being followed, deleting it from the self.main_window.user_state.shows
		'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("+ add")
		self.ui.add_button.setStyleSheet("background-color: " + MAIN_COLOR)

		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		name = self.main_window.user_state.remove_show(name) # dont remove assignment (it returns none in case of failure to remove)
		self.main_window.user_state.save_state()
		print ("Removed: " + name) if name else "Already removed"

		self.ui.add_button.clicked.connect(self.add_show)

			

