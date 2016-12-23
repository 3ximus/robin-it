
'''
GUI for the TV Shows main menu
Latest Update - v1.0
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '1.0'

# TOOLS
import datetime
import subprocess
from functools import partial
from time import sleep

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QMainWindow, QSpacerItem, QWidget
from PyQt5.QtCore import QSize

import settings
from gui.gui_func import begin_hover, clickable, download_object, end_hover
# IMPORT FORMS
from gui.resources.show_banner_widget import Ui_show_banner_widget
from gui.resources.shows_menu import Ui_shows_menu
from gui.resources.episode_download_widget import Ui_episode_download_widget
from gui.resources.torrent_selection_window import Ui_torrent_selection_window
from gui.resources.torrent_row_widget import Ui_torrent_row_widget
from gui.resources.show_scheduled_widget import Ui_show_scheduled_widget
from gui.show_window import ShowWindow
# LIBS IMPORT
from libs.loading import progress_bar
from libs.thread_decorator import threaded
from libs.tvshow import search_for_show


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
		self.ui.clear_button_1.hide()
		self.ui.clear_button_2.hide()
		self.ui.clear_button_3.hide()
		self.ui.clear_button_4.hide()
		self.ui.clear_button_5.hide()

		self.ui.back_button_0.clicked.connect(self.go_back)
		self.ui.back_button_1.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_2.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_3.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_4.clicked.connect(partial(self.go_to, index=0))
		self.ui.back_button_5.clicked.connect(partial(self.go_to, index=0))

		self.ui.stats_button.clicked.connect(partial(self.go_to, index=3))
		self.ui.calendar_button.clicked.connect(partial(self.go_to, index=5))
		self.ui.downloads_button.clicked.connect(self.load_downloads)

		self.ui.myshows_button.clicked.connect(self.load_my_shows)
		self.ui.unwatched_checkbox.stateChanged.connect(self.set_unwatched_filter)

		self.ui.filter_box.textChanged.connect(self.update_filter)
		self.ui.showfilter_box.textChanged.connect(self.update_shows)
		self.ui.downloadsfilter_box.textChanged.connect(self.update_downloads)
		# use 0 for search_box and 1 for search_box_2
		self.ui.search_box.textChanged.connect(partial(self.update_search, 0))
		self.ui.search_box_2.textChanged.connect(partial(self.update_search, 1))

		self.search_results = []
		self.filter_by_unwatched = False

		self.ui.pending_downloads_label.setStyleSheet("background-color: " + settings._GREEN_COLOR)
		if self.user_state.pending_download == {}:
			self.ui.pending_downloads_label.hide()
		else:
			self.ui.pending_downloads_label.setText("%d Pending Downloads" % len(self.user_state.pending_download.keys()))
			self.ui.downloads_button.setStyleSheet("background-color: " + settings._YELLOW_COLOR)

		# updates the shows if they have not been updated for a while, specifically (settings._UPDATE_SHOW_INTERVAL)
		for show in self.user_state.shows.values():
			if show.last_updated:
				if abs(show.last_updated - datetime.date.today()) > datetime.timedelta(settings.config['update_show_interval']):
					self.update_show_info(show)

		self.col = 0
		self.row = 0
		self.loaded_results=0
		self.loaded_layouts = []

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
		self.loaded_layouts = [self.ui.results_layout,]

	@threaded
	def _search_thread(self, text):
		'''Searches for TV shows by given keywords
			Emits self.search_complete when finished
		'''
		results = search_for_show(text, apikey=settings._TVDB_API_KEY)
		self.search_complete.emit(results)

	@threaded
	def update_show_info(self, show):
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
		max_columns = (self.size().width() - settings._MARGIN_SIZES) / widget.size().width()
		col = self.col % max_columns
		if col == 0: self.row +=1
		layout.addWidget(widget, int(self.row), self.col % max_columns)
		self.col += 1

	def resizeEvent(self, event):
		pass # TODO do updates from time to time here see issues #27 and #63

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
		if index==0:
			self.ui.search_box.setFocus()
			self.loaded_layouts = []

	def load_my_shows(self):
		'''Load shows and got to page 2'''
		self.ui.stackedWidget.setCurrentIndex(2)
		self.loaded_layouts = [self.ui.myshows_layout,]
		self.update_shows()
		self.ui.showfilter_box.setFocus()

	def load_downloads(self):
		self.ui.stackedWidget.setCurrentIndex(4)
		self.loaded_layouts = [self.ui.pending_layout,self.ui.scheduled_layout, self.ui.scheduled_shows_layout]
		self.update_downloads()
		self.ui.downloadsfilter_box.setFocus()

	def set_unwatched_filter(self):
		'''Load only the shows with unwatched episodes'''
		self.filter_by_unwatched = self.ui.unwatched_checkbox.isChecked()
		self.update_shows()

	def update_shows(self):
		'''Updates my shows content based on the filter'''
		try:
			if self.ui.stackedWidget.currentIndex() == 2: # my shows page
				if self.ui.showfilter_box.text() == "":
					self.ui.clear_button_2.hide()
				else:
					self.ui.clear_button_2.show()
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

	def update_downloads(self):
		'''Updates Labels and download buttons'''
		if self.ui.stackedWidget.currentIndex() == 4:
			self.clear_layout(self.ui.pending_layout)
			self.clear_layout(self.ui.scheduled_layout)
			self.clear_layout(self.ui.scheduled_shows_layout)

			# filter text clear button
			if self.ui.downloadsfilter_box.text() == "": self.ui.clear_button_4.hide()
			else: self.ui.clear_button_4.show()

			# -- pending downloads
			if self.user_state.pending_download == {}:
				# main show menu
				self.ui.pending_downloads_label.hide()
				self.ui.downloads_button.setStyleSheet("background-color: " + settings._GREEN_COLOR)
				# download menu
				self.ui.pending_label.hide()
			else:
				# main show menu
				self.ui.pending_downloads_label.show()
				self.ui.pending_downloads_label.setText("%d Pending Downloads" % len(self.user_state.pending_download.keys()))
				self.ui.downloads_button.setStyleSheet("background-color: " + settings._YELLOW_COLOR)
				# download menu
				self.ui.pending_label.show()
				items = self.user_state.find_item(self.ui.downloadsfilter_box.text(),
												lst=self.user_state.pending_download,
												key=lambda x: x.tv_show.name,
												return_key=True)
				for episode, tor_list in items:
					self.add_to_layout(self.ui.pending_layout, EpisodeDownloadWidget(episode, tor_list, self))

			# -- scheduled episodes
			if self.user_state.scheduled == []:
				self.ui.scheduled_label.hide()
			else:
				self.ui.scheduled_label.show()
				# TODO EpisodeDownloadWidget needs special condition for this case
				#items = self.user_state.find_item(self.ui.downloadsfilter_box.text(), lst=self.user_state.scheduled)
				#for episode in items:
				#	self.add_to_layout(self.ui.scheduled_layout, EpisodeDownloadWidget(episode, None, self))

			# -- scheduled shows
			if self.user_state.scheduled_shows == []:
				self.ui.scheduled_shows_label.hide()
			else:
				self.ui.scheduled_shows_label.show()
				items = self.user_state.find_item(self.ui.downloadsfilter_box.text(), lst=self.user_state.scheduled_shows)
				for show in items:
					self.add_to_layout(self.ui.scheduled_shows_layout,
					                   ShowScheduledWidget(show, self.user_state, self))


	def update_filter(self):
		'''Filters the news and updates box'''
		print self.ui.filter_box.text()

	def update_search(self, entity):
		'''Maintains search boxes from both stack pages in sync, entity identifies wich search_box called the update'''
		if entity == 0:
			self.ui.search_box_2.setText(self.ui.search_box.text())
		else:
			self.ui.search_box.setText(self.ui.search_box_2.text())
		if self.ui.search_box.text() != "":
			self.ui.clear_button_1.show()
			self.ui.clear_button_5.show()
		else:
			self.ui.clear_button_1.hide()
			self.ui.clear_button_5.hide()

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
		self.show_window = None

		self.ui = Ui_show_banner_widget()
		self.ui.setupUi(self)

		name = self.tvshow['seriesname'] if type(self.tvshow) == dict else self.tvshow.real_name
		self.ui.name_label.setText('%s' % name)
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
			self.ui.download_button.clicked.connect(self.schedule_show)
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

	def schedule_show(self):
		self.user_state.schedule(self.tvshow)
		self.user_state.save_state()
		self.window.ui.statusbar.showMessage("Scheduled %s for download" % self.tvshow.name)

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

class EpisodeDownloadWidget(QWidget):
	'''Small banner to identify an episode in the downloads list

	Parameters:
		episode -- Episode class instance
		torrent_list -- List with torrents gathered

		The whole widget is clickable displaying a list of torrents to choose from
		Emits image_loaded signal when the episode image is loaded
	'''
	image_loaded = QtCore.pyqtSignal(object)

	def __init__(self, episode, torrent_list, window):
		super(EpisodeDownloadWidget, self).__init__()
		self.episode = episode
		self.torrent_list = torrent_list
		self.window = window
		self.torrent_selection_window = None

		self.ui = Ui_episode_download_widget()
		self.ui.setupUi(self)

		self.ui.download_button.clicked.connect(self.download_episode)
		self.ui.delete_button.clicked.connect(self.remove)
		self.image_loaded.connect(self.load_image)
		self.download_image(self.episode.image)

		self.ui.name_label.setText('[%02d] %s' % (int(self.episode.episode_number), self.episode.name))
		self.ui.info_label.setText('%s %s' % (self.episode.airdate, self.episode.rating))
		self.ui.show_label.setText(self.episode.tv_show.name)

		clickable(self).connect(self.display_torrent_selection_window)

	def download_episode(self, torrent=None):
		'''Button that overrides the min seed requirement'''
		if not torrent:
			torrent = max(self.torrent_list, key=lambda x: x.seeds) # get max by seeds

		self.window.ui.statusbar.showMessage("Downloading: %s" % torrent.name)
		print "Downloading: %s\n\t-> Seeds: %d, Host: %s" % (torrent.name, torrent.seeds, torrent.host)
		subprocess.Popen([settings.config['client_application'],torrent.magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		self.remove()

	def remove(self):
		self.window.user_state.remove_pending(self.episode)
		self.window.user_state.save_state()
		self.window.update_downloads()

	@threaded
	def download_image(self, url):
		'''Thread to downlaod episode image'''
		if not url: return
		try:
			data = download_object(url, cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None)
			self.image_loaded.emit(data)
		except IOError: print "Error Loading episode image url: %s" % url
		except RuntimeError: pass # image loaded after the window was closed

	def load_image(self, data):
		'''Triggered by image_loaded signal. Loads image to the widget'''
		image=QPixmap()
		image.loadFromData(data)
		self.ui.image.setPixmap(image)

	def display_torrent_selection_window(self):
		self.window.setEnabled(False)
		self.torrent_selection_window = TorrentSelectionWindow(self.torrent_list, self.window, self)
		self.torrent_selection_window.show()
		self.torrent_selection_window.move(self.window.pos()+self.window.rect().center()-self.torrent_selection_window.rect().center()) # position login window

class TorrentSelectionWindow(QMainWindow):
	'''Window with list of torrents to download'''

	def __init__(self, torrent_list, parent_window, episode_widget=None):
		super(TorrentSelectionWindow, self).__init__()
		self.torrent_list = torrent_list
		self.parent_window = parent_window
		self.episode_widget = episode_widget

		self.ui = Ui_torrent_selection_window()
		self.ui.setupUi(self)
		max_torname_len = len(max(torrent_list, key=lambda x: len(x.name)).name)
		self.setMinimumSize(QSize(max_torname_len * 8 + settings._BASE_SIZE_TORRENT_WINDOW,0))

		for torrent in self.torrent_list:
			self.ui.torrent_layout.addWidget(TorrentRow(torrent, self))

		self.ui.back_button.clicked.connect(self.go_back)

	def go_back(self):
		self.parent_window.setEnabled(True)
		self.close()
		self.destroy()

class TorrentRow(QWidget):
	'''Window with list of torrents to download'''

	def __init__(self, torrent, window):
		super(TorrentRow, self).__init__()
		self.torrent = torrent
		self.window = window

		self.ui = Ui_torrent_row_widget()
		self.ui.setupUi(self)

		self.ui.name_label.setText(self.torrent.name)
		self.ui.info_label.setText(" | %8s | %5d | %5d | %10s | %s" % (
			self.torrent.size, self.torrent.seeds, self.torrent.peers, self.torrent.age, self.torrent.host_name))
		self.ui.download_button.clicked.connect(self.download)

	def download(self):
		self.window.episode_widget.download_episode(torrent=self.torrent)
		self.window.go_back()

class ShowScheduledWidget(QWidget):
	'''Small banner to identify a scheduled show

	Parameters:
		tvshow -- search result to load the banner from or a Show instance
		user_state -- UserContent class

		The whole widget is clickable displaying a Show Window with the tvshow info
		Has an add button to add the show to the followed shows
		Emits banner_loaded signal when the banner image is loaded
	'''
	banner_loaded = QtCore.pyqtSignal(object)

	def __init__(self, tvshow, user_state, window):
		super(ShowScheduledWidget, self).__init__()
		self.tvshow = tvshow
		self.user_state = user_state
		self.window = window
		self.show_window = None

		self.ui = Ui_show_scheduled_widget()
		self.ui.setupUi(self)

		self.ui.name_label.setText('%s' % self.tvshow.name)
		clickable(self).connect(self.view_show)

		self.banner_loaded.connect(self.load_banner)
		self.download_banner(self.tvshow.banner)

		self.ui.counter_label.setText("0")

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
