
'''
GUI for a TV Show window
Latest Update - v0.6
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.6'

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
import math
import urllib

# FIXED VALUES
MAIN_COLOR =  "#03a662"
RED_COLOR =  "#bf273d"
BLUR_RADIOUS = 10
DARKNESS = 0.6
SEASON_MAX_COL = 4
EPISODE_MAX_COL = 3

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
	'''Function to apply filter to an image in the form of binary data'''
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
	'''Main window of a TV Show

	Parameters:
		user_state -- instance of UserContent
		tvshow -- result from a tvshow search or Show class

		Displays most of the show info

		Emits multiple signals:
			show_loaded -- after show info is loaded
			background_loaded  -- main tvshow poster to use as background is loaded
	'''

	show_loaded = QtCore.pyqtSignal()
	background_loaded = QtCore.pyqtSignal(object)
	update_shout = QtCore.pyqtSignal()

	def __init__(self, tvshow, user_state):
		super(ShowWindow, self).__init__()
		self.user_state = user_state

		# set up UI from QtDesigner
		self.ui = Ui_show_window()
		self.ui.setupUi(self)

		self.update_shout.connect(self.update_me)

		self.ui.back_button.clicked.connect(self.close)
		self.ui.add_button.clicked.connect(self.add_show)
		self.ui.mark_button.clicked.connect(self.toogle_watched)
		
		self.background = None
		# Grid placement stuff
		self.season_col = 0
		self.season_row = 0
		self.episode_col = 0
		self.episode_row = 0

		if type(tvshow) == dict:
			if not self.user_state.is_tracked(tvshow['seriesname']):
				# show is not tracked and is search result
				self.ui.showname_label.setText("// %s" % tvshow['seriesname'])
				self.ui.statusbar.showMessage("Loading \"%s\" page..." % tvshow['seriesname'])
				self.show_loaded.connect(self.load_show) # fills info on gui after the show info is retrieved
				self.get_show_data(tvshow['seriesname'])
				return # everyithing done in this case / prevente rest of the code execution
			else:
    			# show is tracked but search result, get the followed show instance instead
				self.tvshow = self.user_state.shows[tvshow['seriesname']]
		else:
    		# show is tracked -- all is good!
			self.tvshow = tvshow
		# this in both cases where it is tracked
		self.update_me()
		self.load_show()

	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if not self.user_state.is_tracked(self.tvshow.real_name):
			self.add_show()
		self.user_state.save_state()
		if self.tvshow.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + MAIN_COLOR)

	@threaded
	def get_show_data(self, name):
		'''Loads the show info from the database'''
		self.tvshow = Show(name, cache=self.user_state.cache_dir)
		self.show_loaded.emit()
		print "Show Loaded: %s" % name

	def load_show(self):
		'''Triggered by the show_loaded signal

			Fills in the info loaded
			Starts background image download
		'''
		self.ui.statusbar.showMessage("Loading info...") # initial message

		if self.tvshow.poster: # load background
			self.background_loaded.connect(self.load_background)
			download_image(self.background_loaded, self.tvshow.poster, filters=True)
			
		if self.user_state.is_tracked(self.tvshow.name):
    			self.make_del_button()

		# fill seasons
		self.display_seasons()
		
		self.ui.showname_label.setText("// %s" % self.tvshow.name)
		self.ui.genre_label.setText('genre - %s' % self.tvshow.genre)
		self.ui.network_label.setText('network - %s' % self.tvshow.network)
		self.ui.airday_label.setText('air day - %s : %s' % (self.tvshow.air_dayofweek, self.tvshow.air_time))
		self.ui.runtime_label.setText('runtime - %s min' % self.tvshow.runtime)
		self.ui.status_label.setText('status - %s' % self.tvshow.status)
		self.ui.imdb_label.setText('<a href="%s"><span style=" text-decoration: underline; color:#03a662;">imdb</span></a> - %s' % (self.tvshow.imdb_id, self.tvshow.rating))
		self.ui.description_box.setText(self.tvshow.description)

	def display_seasons(self):
		'''Adds clickable seasons posters to the window'''
		c = len(self.tvshow.seasons) - len(self.tvshow.seasons)%SEASON_MAX_COL
		for i, s in enumerate(self.tvshow.seasons):
			season = SeasonWidget(s, self)
			clickable(season).connect(partial(self.display_episodes, sid=(s.s_id-1))) # 1 based
			# this is a temporary workaround for seasons display
			if i < c: self.ui.seasons_layout.addWidget(season, self.season_row, self.season_col%SEASON_MAX_COL)
			else: self.ui.last_row_seasons_layout.addWidget(season, self.season_row, self.season_col%SEASON_MAX_COL)
			self.season_col+=1
			if self.season_col%SEASON_MAX_COL==0: self.season_row+=1

	def display_episodes(self, sid):
    		'''Fills the GUI with episodes from selected season'''
		self.episode_col = 0
		self.episode_row = 0
		for i in reversed(range(self.ui.episodes_layout.count())): # clear previous episodes displayed
			self.ui.episodes_layout.itemAt(i).widget().setParent(None)
			
		c = len(self.tvshow.seasons[sid].episodes) - len(self.tvshow.seasons[sid].episodes)%EPISODE_MAX_COL
		for i, e in enumerate(self.tvshow.seasons[sid].episodes):
			if i < c: self.ui.episodes_layout.addWidget(EpisodeWidget(e, self), self.episode_row, self.episode_col%EPISODE_MAX_COL)
			else:  self.ui.last_row_episodes_layout.addWidget(EpisodeWidget(e, self), self.episode_row, self.episode_col%EPISODE_MAX_COL)
			self.episode_col+=1
			if self.episode_col%EPISODE_MAX_COL==0: self.episode_row+=1

	def load_background(self, data):
		'''Triggered by background_loaded signal.
			Loads window background from downloaded background image
		'''
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

	def add_show(self):
		'''Triggered by clicking on self.ui.add_button. Adds show to be tracked'''
		self.user_state.add_show(self.tvshow.name)
		self.user_state.save_state()
		print "Added: " + self.tvshow.name
		self.make_del_button()

	def make_del_button(self):
		'''Transforms the add button into a delete button'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("-del")
		self.ui.add_button.setStyleSheet("background-color: " + RED_COLOR)
		self.ui.add_button.clicked.connect(self.delete_show)

	def delete_show(self):
		'''Triggered by clicking on the add button when this show is added
		
			Stops show from being followed, deleting it from the self.user_state.shows
		'''
		self.ui.add_button.clicked.disconnect()
		self.ui.add_button.setText("+ add")
		self.ui.add_button.setStyleSheet("background-color: " + MAIN_COLOR)

		name = self.user_state.remove_show(self.tvshow.real_name) # dont remove assignment (it returns none in case of failure to remove)
		self.user_state.save_state()
		print ("Removed: " + name) if name else "Already removed"

		self.ui.add_button.clicked.connect(self.add_show)

	def toogle_watched(self):
		'''Toogles watdched state'''
		self.tvshow.toogle_watched()
		self.update_shout.emit() #update button

class SeasonWidget(QWidget):
	'''Season Widget class

	Parameters:
		season -- Season class instance

		Emits poster_loaded signal when season poster is loaded
	'''
	poster_loaded = QtCore.pyqtSignal(object)
	def __init__(self, season, window):
		super(SeasonWidget, self).__init__()
		self.season = season
		self.window = window

		self.ui = Ui_season_banner_widget()
		self.ui.setupUi(self)

		self.update_me()
		self.window.update_shout.connect(self.update_me)
		self.ui.mark_button.clicked.connect(self.toogle_season)
		self.poster_loaded.connect(self.load_poster)
		if len(self.season.poster) > 0:
    			self.download_poster(self.season.poster[0])
			
	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if self.season.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + MAIN_COLOR)

	@threaded
	def download_poster(self, url):
		'''Thread to download season poster'''
		if not url: return
		try: data = urllib.urlopen(url).read()
		except IOError: print "Error Loading season poster url: %s" % url
		self.poster_loaded.emit(data)

	def load_poster(self, data):
		'''Load poster from downloaded data to the widget'''
		poster=QPixmap()
		poster.loadFromData(data)
		self.ui.poster.setPixmap(poster)

	def toogle_season(self):
		'''Toogle season watched state'''
		self.season.toogle_watched()
		self.window.update_shout.emit()

class EpisodeWidget(QWidget):
	'''Episode Widget class

	Parameters:
		episode -- Episode class instance

		Emits image_loaded signal when the episode image is loaded
	'''
	image_loaded = QtCore.pyqtSignal(object)
	def __init__(self, episode, window):
		super(EpisodeWidget, self).__init__()
		self.episode = episode
		self.window = window

		self.ui = Ui_episode_banner_widget()
		self.ui.setupUi(self)

		self.update_me()
		self.ui.mark_button.clicked.connect(self.toogle_episode)
		self.window.update_shout.connect(self.update_me)
		self.image_loaded.connect(self.load_image)
		self.download_image(self.episode.image)
		
		self.ui.name_label.setText('< %s - %s >' % (self.episode.episode_number, self.episode.name))

	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if self.episode.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + MAIN_COLOR)
			
	@threaded
	def download_image(self, url):
		'''Thread to downlaod episode image'''
		if not url: return
		try: data = urllib.urlopen(url).read()
		except IOError: print "Error Loading episode image url: %s" % url
		self.image_loaded.emit(data)

	def load_image(self, data):
		'''Triggered by image_loaded signal. Loads image to the widget'''
		image=QPixmap()
		image.loadFromData(data)
		self.ui.image.setPixmap(image)

	def toogle_episode(self):
		'''Toogle season watched state'''
		self.episode.toogle_watched()
		self.window.update_shout.emit()