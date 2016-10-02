
'''
GUI for the TV Shows main menu
Latest Update - v0.3
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.3'

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPixmap

# IMPORT FORMS
from gui.resources.shows_menu import Ui_shows_menu
from gui.resources.show_banner_widget import Ui_show_banner_widget

# LIBS IMPORT
from gui_func import clickable
from show_window import ShowWindow
from libs.tvshow import search_for_show
from libs.thread_decorator import threaded
from libs.loading import progress_bar

# TOOLS
from functools import partial
import urllib

class ShowWidget(QWidget):
	banner_loaded = QtCore.pyqtSignal(object)

	def __init__(self, tvshow):
		super(ShowWidget, self).__init__()
		self.tvshow = tvshow

		self.ui = Ui_show_banner_widget()
		self.ui.setupUi(self)
		self.ui.name_label.setText('< %s >' % self.tvshow['seriesname'])

		clickable(self).connect(self.view_show)
		self.ui.add_button.clicked.connect(self.add_show)

		if 'banner' in self.tvshow.keys():
			self.banner_loaded.connect(self.load_banner)
			self.download_banner("http://thetvdb.com/banners/" + self.tvshow['banner']) #FIXME harcoding is bad for your health

	@threaded
	def download_banner(self, url):
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

class ShowsMenu(QMainWindow):
	search_complete_signal = QtCore.pyqtSignal(object)

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
		self.ui.statusbar.showMessage("Searching for %s..." % self.ui.search_box.text())
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
				banner = ShowWidget(r)
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
