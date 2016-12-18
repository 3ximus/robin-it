
'''
GUI for a TV Show window
Latest Update - v1.0
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '1.0'

# PYQT5 IMPORTS
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush

# IMPORT FORMS
from gui.resources.show import Ui_show_window
from gui.resources.season_banner_widget import Ui_season_banner_widget
from gui.resources.episode_banner_widget import Ui_episode_banner_widget

# LIBS IMPORT
from gui.gui_func import clickable, download_object, begin_hover, end_hover
from libs.tvshow import Show
from libs.thread_decorator import threaded
import settings

# TOOLS
from functools import partial
from PIL import Image, ImageFilter
from cStringIO import StringIO

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

	def __init__(self, tvshow, user_state, origin_window):
		super(ShowWindow, self).__init__()
		self.user_state = user_state
		self.origin_window = origin_window

		# set up UI from QtDesigner
		self.ui = Ui_show_window()
		self.ui.setupUi(self)

		self.update_shout.connect(self.update_me)

		self.ui.back_button.clicked.connect(self.close)
		self.ui.add_button.clicked.connect(self.add_show)
		self.ui.mark_button.clicked.connect(self.toogle_watched)

		self.ui.add_button.setEnabled(False)
		self.ui.mark_button.setEnabled(False)
		self.ui.episodes_label.setText("")

		self.background_data = None
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
				return # everything done in this case / prevente rest of the code execution
			else:
				# show is tracked but search result, get the followed show instance instead
				self.tvshow = self.user_state.shows[tvshow['seriesname']]
		else:
			# show is tracked -- all is good!
			self.tvshow = tvshow
		# this in both cases where it is tracked
		self.update_me()
		self.load_show()

		# TODO uncoment this: self.ui.force_update_button.connect(self.force_update)

	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if not self.user_state.is_tracked(self.tvshow.real_name):
			self.add_show()
		self.user_state.save_state()
		if self.tvshow.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._GREEN_COLOR)
		self.origin_window.update_shows()

	@threaded
	def force_update(self):
		self.tvshow.update_info()

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
			self.download_image(self.tvshow.poster)

		if self.user_state.is_tracked(self.tvshow.name):
			self.make_del_button()

		# fill seasons
		self.display_seasons()

		if self.tvshow.last_updated: self.ui.last_updated_label.setText("last updated %s" % self.tvshow.last_updated)
		self.ui.showname_label.setText("// %s" % self.tvshow.name)
		self.ui.genre_label.setText('genre\t\t%s' % self.tvshow.genre)
		self.ui.network_label.setText('network\t\t%s' % self.tvshow.network)
		self.ui.airday_label.setText('air day\t\t%s : %s' % (self.tvshow.air_dayofweek, self.tvshow.air_time))
		self.ui.runtime_label.setText('runtime\t\t%s min' % self.tvshow.runtime)
		self.ui.status_label.setText('status\t\t%s' % self.tvshow.status)
		self.ui.imdb_label.setText('<a href="%s"><span style=" text-decoration: underline; color:#03a662;">imdb</span></a>\t\t%s' % (self.tvshow.imdb_id, self.tvshow.rating))
		self.ui.description_box.setText(self.tvshow.description)

		self.ui.add_button.setEnabled(True)
		self.ui.mark_button.setEnabled(True)

	def display_seasons(self):
		'''Adds clickable seasons posters to the window'''
		c = len(self.tvshow.seasons) - len(self.tvshow.seasons)%settings._SEASON_MAX_COL
		for i, s in enumerate(self.tvshow.seasons):
			season = SeasonWidget(s, self)
			clickable(season).connect(partial(self.display_episodes, sid=(s.s_id-1))) # 1 based
			# this is a temporary workaround for seasons display
			if i < c: self.ui.seasons_layout.addWidget(season, self.season_row, self.season_col%settings._SEASON_MAX_COL)
			else: self.ui.last_row_seasons_layout.addWidget(season, self.season_row, self.season_col%settings._SEASON_MAX_COL)
			self.season_col+=1
			if self.season_col%settings._SEASON_MAX_COL==0: self.season_row+=1

	def display_episodes(self, sid):
		'''Fills the GUI with episodes from selected season'''
		self.episode_col = 0
		self.episode_row = 0
		self.ui.episodes_label.setText("[ s%02d episodes ]" % (sid+1))
		self.clear_layout(self.ui.episodes_layout)
		self.clear_layout(self.ui.last_row_episodes_layout)

		c = len(self.tvshow.seasons[sid].episodes) - len(self.tvshow.seasons[sid].episodes)%settings._EPISODE_MAX_COL
		for i, e in enumerate(self.tvshow.seasons[sid].episodes):
			if i < c: self.ui.episodes_layout.addWidget(EpisodeWidget(e, self), self.episode_row, self.episode_col%settings._EPISODE_MAX_COL)
			else:  self.ui.last_row_episodes_layout.addWidget(EpisodeWidget(e, self), self.episode_row, self.episode_col%settings._EPISODE_MAX_COL)
			self.episode_col+=1
			if self.episode_col%settings._EPISODE_MAX_COL==0: self.episode_row+=1

	def clear_layout(self, layout):
		'''Clear given layout'''
		for i in reversed(range(layout.count())): # clear previous episodes displayed
			layout.itemAt(i).widget().deleteLater()

	@threaded
	def download_image(self, url):
		'''Thread to download image, emits signal when complete'''
		if not url: return
		data = download_object(url, cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None)
		data = self._apply_filters(data)
		self.background_loaded.emit(data)

	def _apply_filters(self, data):
		'''Function to apply filter to an image in the form of binary data'''
		data = StringIO(data)
		img = Image.open(data)
		img = img.point(lambda x: x*settings._DARKNESS) # darken
		img = img.filter(ImageFilter.GaussianBlur(settings._BLUR_RADIOUS)) # blur
		tmp_data = StringIO()
		img.save(tmp_data, format='PNG')
		data = tmp_data.getvalue()
		tmp_data.close()
		return data

	def load_background(self, data):
		'''Triggered by background_loaded signal.
			Loads window background from downloaded background image
		'''
		palette = QPalette()
		self.background_data = data
		background = QPixmap()
		background.loadFromData(self.background_data)
		self.back_ratio = background.size().width()/float(background.size().height())
		background=background.scaled(QtCore.QSize(self.size().width(),self.size().width()/float(self.back_ratio)))
		palette.setBrush(QPalette.Background, QBrush(background))
		self.setPalette(palette)
		self.ui.statusbar.clearMessage()
		# Forces scrollareas to be transparent
		self.ui.scrollArea_2.setStyleSheet("background-color: transparent;")
		self.ui.scrollArea_3.setStyleSheet("background-color: transparent;")

	def resizeEvent(self, event):
		'''Called when resize is made'''
		# NOTE if this causes performance issues later on, make the resize happen in sparse intervals
		if self.background_data:
			palette = QPalette()
			background = QPixmap()
			background.loadFromData(self.background_data)
			# TODO if the background reaches maximum its maximum height, then resize the width instead
			background=background.scaled(QtCore.QSize(self.size().width(),self.size().width()/float(self.back_ratio)))
			palette.setBrush(QPalette.Background, QBrush(background))
			self.setPalette(palette)

	def add_show(self):
		'''Triggered by clicking on self.ui.add_button. Adds show to be tracked'''
		self.ui.statusbar.showMessage("Adding \"%s\"..." % self.tvshow.name)
		self.user_state.add_show(show=self.tvshow)
		self.user_state.save_state()
		print "Added: " + self.tvshow.name
		self.ui.statusbar.clearMessage()
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

		name = self.user_state.remove_show(self.tvshow.real_name) # dont remove assignment (it returns none in case of failure to remove)
		self.user_state.save_state()
		print ("Removed: " + name) if name else "Already removed"

		self.ui.add_button.clicked.connect(self.add_show)

	def toogle_watched(self):
		'''Toogles watdched state'''
		self.tvshow.toogle_watched()
		self.update_shout.emit() #update button

	def closeEvent(self, event):
		self.clear_layout(self.ui.episodes_layout)
		self.clear_layout(self.ui.last_row_episodes_layout)
		self.clear_layout(self.ui.seasons_layout)
		self.clear_layout(self.ui.last_row_seasons_layout)
		self.deleteLater()

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
		self.ui.download_button.setStyleSheet("background-color: " + settings._MAIN_COLOR)
		if len(self.season.poster) > 0:
			self.download_poster(self.season.poster[0])

	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if self.season.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._GREEN_COLOR)

	@threaded
	def download_poster(self, url):
		'''Thread to download season poster'''
		if not url: return
		try:
			data = download_object(url, cache_dir=settings.config['cache_dir'] if settings.config.has_property('cache_dir') else None)
			self.poster_loaded.emit(data)
		except IOError: print "Error Loading season poster url: %s" % url
		except RuntimeError: pass # image loaded after the window was closed

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

		begin_hover(self).connect(self.show_details)
		end_hover(self).connect(self.hide_details)
		self.ui.filler.hide()
		self.ui.description.hide()

		self.update_me()
		self.ui.mark_button.clicked.connect(self.toogle_episode)
		self.window.update_shout.connect(self.update_me)
		self.image_loaded.connect(self.load_image)
		self.download_image(self.episode.image)

		self.ui.name_label.setText('[%02d] %s' % (int(self.episode.episode_number), self.episode.name))
		self.ui.info_label.setText('%s %s' % (self.episode.airdate, self.episode.rating))
		self.ui.description.setText(self.episode.description)
		self.ui.download_button.setStyleSheet("background-color: " + settings._MAIN_COLOR)
		self.ui.filler.setStyleSheet("background-color: " + settings._MAIN_COLOR_RGB_ALPHA)

	def update_me(self):
		'''Triggered by update_shout signal. Update some gui elements that may need sync'''
		if self.episode.watched:
			self.ui.mark_button.setText("umark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._RED_COLOR)
		else:
			self.ui.mark_button.setText("mark")
			self.ui.mark_button.setStyleSheet("background-color: " + settings._GREEN_COLOR)

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

	def toogle_episode(self):
		'''Toogle season watched state'''
		self.episode.toogle_watched()
		self.window.update_shout.emit()

	def show_details(self):
		self.ui.filler.show()
		self.ui.description.show()
		self.ui.name_label.hide()

	def hide_details(self):
		self.ui.filler.hide()
		self.ui.description.hide()
		self.ui.name_label.show()