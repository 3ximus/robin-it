
'''
GUI for a TV Show window
Latest Update - v0.3
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.3'

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush

# IMPORT FORMS
from gui.resources.show import Ui_show_window
from gui.resources.season_banner_widget import Ui_season_banner_widget
from gui.resources.episode_banner_widget import Ui_episode_banner_widget

# LIBS IMPORT
from gui_func import clickable
from libs.tvshow import Show
from libs.thread_decorator import threaded

# TOOLS
from functools import partial
from PIL import Image, ImageFilter
from cStringIO import StringIO
import urllib

# FIXED VALUES
BLUR_RADIOUS = 10
DARKNESS = 0.6

# --------------------
#       Functions
# --------------------

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

# --------------------
#      Classes 
# --------------------

class ShowWindow(QMainWindow):
	show_loaded = QtCore.pyqtSignal()
	background_loaded = QtCore.pyqtSignal(object)
	update_done = QtCore.pyqtSignal()
	refresh_status = QtCore.pyqtSignal()

	def __init__(self, tvshow):
		super(ShowWindow, self).__init__()

		# set up UI from QtDesigner
		self.ui = Ui_show_window()
		self.ui.setupUi(self)

		self.background = None
		self.ui.showname_label.setText("> %s" % tvshow['seriesname'])

		self.ui.back_button.clicked.connect(self.close)

		self.show_loaded.connect(self.fill_info) # fills info on gui after the show info is retrieved
		self.refresh_status.connect(self.update_status) # updates statusbar while updating show
		self.update_done.connect(self.fill_seasons) # fills gui with info about seasons and episodes

		self.ui.statusbar.showMessage("Loading \"%s\" page..." % tvshow['seriesname'])
		self.load_show(tvshow['seriesname'])

	@threaded
	def load_show(self, name):
		'''Loads show from database'''
		self.tvshow = Show(name, header_only=True)
		self.show_loaded.emit()
		print "Show Loaded: %s" % name

	def fill_info(self):
		'''Fill in info after loaded, starting background download'''
		if self.tvshow.poster: # load background
			self.ui.statusbar.showMessage("Loading Background...")
			self.background_loaded.connect(self.load_background)
			download_image(self.background_loaded, self.tvshow.poster, filters=True)
		self.update_show() #update seasons and episodes

		self.ui.showname_label.setText("> %s" % self.tvshow.name)
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

	def resizeEvent(self, event):
		'''Called when resize is made'''
		if self.background:
			palette = QPalette()
			self.background=self.background.scaled(QtCore.QSize(self.size().width(),self.size().width()/float(self.back_ratio)))
			palette.setBrush(QPalette.Background, QBrush(self.background))
			self.setPalette(palette)

	@threaded
	def update_show(self):
		self.refresh_status.emit()
		self.tvshow.update_info(override_cache='cache/')
		self.update_done.emit()

	def fill_seasons(self):
		'''Fills the GUI with seasons widgets'''
		self.ui.statusbar.clearMessage()
		for s in self.tvshow.seasons:
			season = SeasonWidget(s)
			clickable(season).connect(partial(self.fill_episodes, sid=(s.s_id-1)))
			self.ui.seasons_layout.addWidget(season)

	def fill_episodes(self, sid):
		'''Fills the GUI with episodes from selected season'''
		for i in reversed(range(self.ui.episodes_layout.count())): # clear previous episodes displayed
			self.ui.episodes_layout.itemAt(i).widget().setParent(None)
		for e in self.tvshow.seasons[sid].episodes:
			self.ui.episodes_layout.addWidget(EpisodeWidget(e))

	def update_status(self):
		self.ui.statusbar.showMessage("Loading info...") # initial message

class EpisodeWidget(QWidget):
	image_loaded = QtCore.pyqtSignal(object)
	def __init__(self, episode):
		super(EpisodeWidget, self).__init__()
		self.episode = episode

		self.ui = Ui_episode_banner_widget()
		self.ui.setupUi(self)

		self.image_loaded.connect(self.load_image)
		self.download_image(self.episode.image)
		self.ui.name_label.setText('< %s - %s >' % (self.episode.episode_number, self.episode.name))

	@threaded
	def download_image(self, url):
		data = urllib.urlopen(url).read()
		self.image_loaded.emit(data)

	def load_image(self, data):
		image=QPixmap()
		image.loadFromData(data)
		self.ui.image.setPixmap(image)

class SeasonWidget(QWidget):
	poster_loaded = QtCore.pyqtSignal(object)
	def __init__(self, season):
		super(SeasonWidget, self).__init__()
		self.season = season

		self.ui = Ui_season_banner_widget()
		self.ui.setupUi(self)

		self.ui.mark_button.clicked.connect(self.mark_show)
		self.poster_loaded.connect(self.load_poster)
		if len(self.season.poster) > 0:
			self.download_poster(self.season.poster[0])

	@threaded
	def download_poster(self, url):
		data = urllib.urlopen(url).read()
		self.poster_loaded.emit(data)

	def load_poster(self, data):
		'''Load poster from downloaded data'''
		poster=QPixmap()
		poster.loadFromData(data)
		self.ui.poster.setPixmap(poster)

	def mark_show(self):
		pass
