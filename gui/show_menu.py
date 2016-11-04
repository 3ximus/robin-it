
'''
GUI for the TV Shows main menu
Latest Update - v0.6
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.6'

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QSpacerItem
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor

# IMPORT FORMS
from gui.resources.shows_menu import Ui_shows_menu
from gui.resources.show_banner_widget import Ui_show_banner_widget

# LIBS IMPORT
from gui_func import clickable, download_object, end_hover, begin_hover
from show_window import ShowWindow
from libs.tvshow import search_for_show
from libs.thread_decorator import threaded
from libs.loading import progress_bar
import settings

# TOOLS
import datetime
from time import sleep
from functools import partial

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
		self.ui.unwatched_checkbox.stateChanged.connect(self.set_unwatched_filter)

		self.ui.filter_box.textChanged.connect(self.update_filter)
		self.ui.showfilter_box.textChanged.connect(self.update_shows)
		self.ui.search_box.textChanged.connect(self.update_search)
		self.ui.search_box_2.textChanged.connect(self.update_search_2)

		self.search_results = []
		self.filter_by_unwatched = False

		for show in self.user_state.shows.values():
			if show.last_updated:
				if abs(show.last_updated - datetime.date.today()) > datetime.timedelta(settings._UPDATE_SHOW_INTERVAL):
					self.update_show(show)

		self.col = 0
		self.row = 0

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

	@threaded
	def update_show(self, show):
		show.update_info()

	def clear_layout(self, layout):
		'''Clears all widgets from given layout'''
		self.col = 0 # reset rows and columns
		self.row = 0
		for i in reversed(range(layout.count())): # clear previous results
			layout.itemAt(i).widget().deleteLater() # forces its deletion
		try: self.all_banners_loaded.disconnect() # disconnect signals in order to not connect duplicates
		except TypeError: pass
		for x in self.search_results:
			try: x.disconnect() # prevent previous search from adding widgets to new search
			except TypeError: continue
			except RuntimeError: continue
		self.ui.statusbar.clearMessage()

	def add_to_layout(self, layout, widget):
		'''Takes the widget to be added and the layout to add it to'''
		layout.addWidget(widget, int(self.row), self.col)
		self.row += 0.5
		self.col = 1 if self.col == 0 else 0
		return

	def display_results(self, results):
		'''Triggered by the self.search_complete signal. Displays TV show results on stack widget page 1

			Cleans the layout and adds show widgets when they finish loading the respective banners.
			Shows without banners are left pending until self.all_banners_loaded signal
			is triggered, displaying the remaining results.
			This is done in order to only display bannerless shows at the end
		'''
		# TODO ditch all this nonsense and just display all results, let images load when they can

		def _status_update():
			'''Updates Status bar loading message with progress_bar'''
			self.loaded_results+=1
			p = 100*self.loaded_results/len(results)
			bar = progress_bar(p, show_percentage=True)
			self.ui.statusbar.showMessage(bar)
			if self.loaded_results == len(results): # clear status bar after completion
				self.ui.statusbar.clearMessage()

		@threaded
		def _wait_for_loading(pending_add):
			'''This thread will simply wait until all shows with banners are loaded
				Emits self.all_banners_loaded when finished
			'''
			counter = settings._RESULTS_TIMEOUT # timeout to prevent hanging
			while counter > 0:
				if self.loaded_results == len(results)-len(pending_add):
					self.all_banners_loaded.emit()
					return
				sleep(1)
				counter -= 1

		def _display_pending(pending):
			'''Triggered by self.all_banners_loaded signal. Display shows without banner'''
			for p in pending: # add the shows without banner at the end
				self.add_to_layout(self.ui.results_layout, p)
				_status_update()

		self.clear_layout(self.ui.results_layout)
		if len(results) == 0: # no results found
			self.ui.results_layout.addWidget(self.ui.noresults_label)
			return
		pending_add = []
		self.all_banners_loaded.connect(partial(_display_pending, pending=pending_add))
		for r in results: # display new results
			banner = ShowWidget(r, self.user_state, self)
			self.search_results.append(banner)
			if 'banner' not in r: # shows without banners added to pending add
				pending_add.append(banner)
			else:
				banner.banner_loaded.connect(partial(self.add_to_layout, layout=self.ui.results_layout, widget=banner))
				banner.banner_loaded.connect(_status_update)

		_wait_for_loading(pending_add) # add bannerless when all other shows are loaded

	def go_back(self):
		'''Closes this window and opens the Main Menu'''
		self.clear_layout(self.ui.myshows_layout)
		self.clear_layout(self.ui.results_layout)
		self.close()
		self.return_to.show()
		self.deleteLater()

	def go_to(self, index):
		'''Got to one of the stacked pages given by index'''
		self.ui.stackedWidget.setCurrentIndex(index)
		if index==0: self.ui.search_box.setFocus()

	def load_my_shows(self):
		'''Load shows and got to page 2'''
		self.ui.stackedWidget.setCurrentIndex(2)
		self.ui.showfilter_box.setFocus()
		self.clear_layout(self.ui.myshows_layout)
		for show in self.user_state.shows.values():
			self.add_to_layout(self.ui.myshows_layout, ShowWidget(show, self.user_state, self))
		pass

	def set_unwatched_filter(self):
		'''Load only the shows with unwatched episodes'''
		self.filter_by_unwatched = self.ui.unwatched_checkbox.isChecked()
		self.update_shows()

	def update_shows(self):
		'''Updates my shows content based on the filter'''
		try:
			if self.ui.stackedWidget.currentIndex() == 2: # my shows page
				self.clear_layout(self.ui.myshows_layout)
				items = self.user_state.find_item(self.ui.showfilter_box.text())
				if not items: return
				if self.filter_by_unwatched: # create list of unwatched
					unwatched = self.user_state.unwatched_shows()
				for s in items:
					if self.filter_by_unwatched and not s in unwatched: # if filter is set but its not an unwatched episode ignore it
						continue
					self.add_to_layout(self.ui.myshows_layout, ShowWidget(s, self.user_state, self))
		except RuntimeError as e: print "RuntimeError:", e

	def update_filter(self):
		'''Filters the news and updates box'''
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
		user_state -- UserContent class

		The whole widget is clickable displaying a Show Window with the tvshow info
		Has an add button to add the show to the followed shows
		Emits banner_loaded signal when the banner image is loaded

		Used in search results
	'''
	banner_loaded = QtCore.pyqtSignal(object)

	def __init__(self, tvshow, user_state, window):
		super(ShowWidget, self).__init__()
		self.tvshow = tvshow
		self.user_state = user_state
		self.window = window

		self.ui = Ui_show_banner_widget()
		self.ui.setupUi(self)

		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		self.ui.name_label.setText('< %s >' % name)
		clickable(self).connect(self.view_show)

		self.ui.add_button.clicked.connect(self.add_show)
		if self.user_state.is_tracked(name):
			self.make_del_button()

		if type(self.tvshow) == dict: # this is a search result
			self.ui.progress_bar.hide()
			self.ui.counter_label.hide()
			if 'banner' in self.tvshow.keys():
				self.banner_loaded.connect(self.load_banner)
				self.download_banner(settings._TVDB_BANNER_PREFIX + self.tvshow['banner'])
		else: # this is a tracked show and not a search result
			self.banner_loaded.connect(self.load_banner)
			self.download_banner(self.tvshow.banner)


			begin_hover(self).connect(self.show_more)
			end_hover(self).connect(self.show_less)

			watched, total = self.tvshow.get_watched_ratio()
			self.ui.counter_label.setText("%d/%d [%d%%]" % (watched, total, float(watched)/total*100))
			self.ui.counter_label.hide()
			self.ui.add_button.hide()
			self.ui.download_button.hide()
			# spacer items dont get a reference from pyuic so we must get it from the layout
			if watched == 0:
				self.ui.progress_bar.hide()
			else:
				for i in range(self.ui.bar_layout.count()):
					if type(self.ui.bar_layout.itemAt(i)) == QSpacerItem:
						width = self.ui.banner.size().width() # small ajustment
						size = width - float(watched)/total * width
						# base size must be 8 pixels otherwise the bound will be passed.. dunno why, it just works
						self.ui.bar_layout.itemAt(i).changeSize(8 if size <= 0 else size,0)
						break
			self.ui.progress_bar.setStyleSheet("background-color: " + settings._GREEN_COLOR)

	@threaded
	def download_banner(self, url):
		'''Thread to download banner, emits self.banner_loaded signal when complete'''
		if not url: return
		data = download_object(url, cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None)
		self.banner_loaded.emit(data)

	def load_banner(self, data):
		'''Triggered by self.banner_loaded signal. Loads the banner from downloaded data'''
		if not data: return # when banner was not loaded or url couldnt be reached
		banner = QPixmap()
		banner.loadFromData(data)
		self.ui.banner.setPixmap(banner)

	def view_show(self):
		'''Triggered clicking on the widget. Displays Show Window'''
		self.show_window = ShowWindow(self.tvshow, self.user_state, self.window)
		self.show_window.show()

	def add_show(self):
		'''Triggered by clicking on self.ui.add_button. Adds show to be tracked'''
		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		self.window.ui.statusbar.showMessage("Adding \"%s\" ..." % name)
		self.user_state.add_show(name)
		self.user_state.save_state()
		print "Added: " + name
		self.window.ui.statusbar.clearMessage()
		self.make_del_button()

	def make_del_button(self):
		'''Transforms the add button into a delete button'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("-del")
		self.ui.add_button.setStyleSheet("background-color: " + settings._RED_COLOR)
		self.ui.add_button.clicked.connect(self.delete_show)

	def delete_show(self):
		'''Triggered by clicking on the add button when this show is added

			Stops show from being followed, deleting it from the self.user_state.shows
		'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("+ add")
		self.ui.add_button.setStyleSheet("background-color: " + settings._GREEN_COLOR)

		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		name = self.user_state.remove_show(name) # dont remove assignment (it returns none in case of failure to remove)
		self.user_state.save_state()
		print ("Removed: " + name) if name else "Already removed"

		self.ui.add_button.clicked.connect(self.add_show)

	def show_more(self):
		if type(self.tvshow) == dict or not self.user_state.is_tracked(self.tvshow.real_name):
			return
		self.ui.counter_label.show()
		self.ui.add_button.show()
		self.ui.download_button.show()

	def show_less(self):
		self.ui.counter_label.hide()
		self.ui.add_button.hide()
		self.ui.download_button.hide()
