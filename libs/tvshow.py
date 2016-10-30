'''
API for getting TV Shows information
Queries http://thetvdb.com/ using  tvdb_api: https://github.com/dbr/tvdb_api
Example usage program in the end
# note that seasons and episodes are indexed with zero base

Latest Update - v1.0
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

from tvdb_api import Tvdb
from tvdb_exceptions import tvdb_error, tvdb_shownotfound, tvdb_attributenotfound
from torrent import Torrent
import datetime
import os
import re

IMDB_TITLE = "http://www.imdb.com/title/"

def search_for_show(search_term):
	'''Auxiliar method to search for TVShows in the database, returns None if no show found'''
	try: return Tvdb(cache=False).search(search_term)
	except tvdb_error: raise NoConnectionException
	except tvdb_shownotfound: return None

class TVError(Exception):
	'''Main Error Class'''
	pass

class NoConnectionException(TVError):
	'''No connection to server error'''
	pass

class Show:
	'''Class Containing Show information

	This class is self updated, once the method update_info is called it updates itself
	'''

	def __init__(self, name, header_only = False, cache=False, banners=False):
		'''Class constructor

		Parameters:
			header_only - does not retrive season and episodes info
			cache - path to cache NOTE: if set, greatly increses performance
			banners - retrieve season banners and posters

		Name must be the only possibility otherwise an error will ocurr (use search_for_show method and
			use 'seriesname' as the name to build this correctly)
		The header only flag only builds the class with Show information and doesn't retrieve seasons
			and episodes info
		'''

		# define class atributes
		self.name = '' # tv show name parsed
		self.real_name = '' # tv show name
		self.description = '' # tv show description
		self.seasons = [] # seasons
		self.genre = '' # genre
		self.runtime = '' # episode times
		self.status = '' # show status (Continuing, Ended)
		self.network = '' # airing network
		self.air_dayofweek = '' # week day of hairing
		self.air_time = '' # hour it airs
		self.rating = '' # imdb rating
		self.actors = '' # actors list
		self.poster = '' # tv show poster
		self.banner = '' # banner
		self.all_images = None # posters fanart banners
		self.imdb_id = '' # imdb id
		self.watched = False
		self.torrent = None
		self.cache=cache
		self.last_updated = None

		if self.cache:
			if not os.path.exists(self.cache):
				os.mkdir(self.cache) # make directory if unexistent

		self.name = name.split('(')[0]
		self.real_name = name
		self.update_info(header_only=header_only, banners=banners) # generate content

	def update_info(self, header_only = False, override_cache=False, banners=False):
		'''Searches thetvdb.com and generates class attributes

		Parameters:
			header_only - does not retrive season and episodes info
			override_cache - path to new cache, ignoring class defined cache NOTE: if set, greatly increses performance
			banners - retrieve season banners and posters

		This method function is responsible for building the entire data structure of a TV Show
		It is mandatory that self.real_name is set otherwise build will fail
		'''
		database = Tvdb(cache = (self.cache if not override_cache else override_cache), banners=banners)

		if not header_only:
			# updates seasons list
			seasons_list = database[self.real_name].keys() # retrieve list of available seasons
			if seasons_list[0] == 0: del(seasons_list[0]) # remove first element if it is season 0
			self.seasons = []
			for i in seasons_list: # generates the seasons list
				new_season = Season(s_id = i, tv_show = self, cache=(self.cache if not override_cache else override_cache))
				self.seasons.append(new_season)

		self.last_updated = datetime.date.today()

		# update TV Show info
		self.description = database[self.real_name]['overview']
		self.genre = database[self.real_name]['genre']
		self.runtime = database[self.real_name]['runtime']
		self.status = database[self.real_name]['status']
		self.network = database[self.real_name]['network']
		self.air_dayofweek = database[self.real_name]['airs_dayofweek']
		self.air_time = database[self.real_name]['airs_time']
		self.rating = database[self.real_name]['rating']
		self.actors = database[self.real_name]['actors']
		self.poster = database[self.real_name]['poster']
		self.banner = database[self.real_name]['banner']
		if banners: self.all_images = database[self.real_name]['_banners']
		imdb_id = database[self.real_name]['imdb_id']
		self.imdb_id = IMDB_TITLE + (imdb_id if imdb_id else '')

	def set_cache_dir(self, new_dir):
		'''Sets the cache to a new directory'''
		self.cache = new_dir
		for s in self.seasons:
			s.cache = new_dir
			for e in s.episodes:
				e.cache = new_dir

	def toogle_watched(self, state=None):
		''' Toogle the watched state, if state is given set the the state to the given one'''
		self.watched = (not self.watched) if state==None else state # toogle watched
		for season in self.seasons: # replicate action to every season
			season.set_watched(self.watched)

	def update_watched(self):
		'''Update watched on the entire tv show

		Propagates decisions to entire show tree
		'''
		seasons_watched = 0
		for season in self.seasons: # for every season on this show
			if season.watched: seasons_watched += 1
		if seasons_watched == len(self.seasons): self.watched = True

	def set_torrent(self, torrent):
		'''Set torrent instance associated with this episode'''
		self.torrent=torrent

	def get_status(self):
		'''Returns the status this show has, in respect to the user'''
		if self.watched:
			if self.status == 'Ended':
				return "completed"
			elif self.status == 'Continuing':
				return "watched"
		else: return "unwatched"
# TODO handle episode air date

	def to_string(self):
		'''Print this class information'''
		print "\t TV Show info:\nName: %s\nGenre: %s\nRuntime: %s\nStatus: %s\nNetwork: %s\nAiring Day: %s\nAir Time: %s\nRating: %s\nPoster: %sBanner: %s\nIMDB Link: %s" % (self.name, self.genre, self.runtime, self.status, self.network, self.air_dayofweek, self.air_time, self.rating, self.poster, self.banner, self.imdb_id)
		print "Description: %s" % self.description.encode('utf-8')

	def get_unwatched_episodes(self):
		'''Returns unwatched episodes

		Return format:
			{season_id:[ep1, ep2, ...], season_id:[...] ...}
		'''
		seasons = {}
		for season in self.seasons:
			episode_list = []
			for episode in season.episodes:
				if not episode.watched: episode_list.append(episode)
			if episode_list != []:
				seasons.update({str(season.s_id):episode_list})
		return seasons

	def get_episodes_list(self):
		'''Returns full list of episodes'''
		episodes_list = []
		for season in self.seasons:
			for episode in season.episodes:
				episodes_list.append(episode)
		return episodes_list

	def get_last_aired(self):
		'''Returns last episode aired'''
		for s in reversed(self.seasons):
			for e in reversed(s.episodes):
				if e.already_aired: return e

class Season():
	'''Class defining a TV Show Season

	Its self updatable with method update_info, this updates every episode information
	'''

	def __init__(self, s_id, tv_show, cache=False, banners=True):
		'''Constructor method

		Parameters:
			cache - path to new cache, ignoring class defined cache NOTE: if set, greatly increses performance
			banners - retrieve season banners and posters
		Must receive a season id number and a tv_show from where this season belongs to
		'''
		self.s_id = s_id # 1 based
		self.episodes = []
		self.poster = [] # list of season poster
		self.poster_wide = [] # list of season wide posters
		self.watched = False
		self.torrent = None
		if tv_show: self.tv_show = tv_show # set show instance
		else: raise TVError("tv_show must be a Show instance") # tv_show cant be None
		self.cache=cache
		self.update_info(cache=cache, banners=banners)

	def to_string(self):
		'''Print this class information'''
		return_string = ''
		for episode in self.episodes: return_string += "%s - %s\n" % (episode.episode_number, episode.name)
		print return_string

	def update_info(self, cache=False, banners=True):
		'''Searches thetvdb.com and updates all episodes it contains

		Parameters:
			cache - path to new cache, ignoring class defined cache NOTE: if set, greatly increses performance
			banners - retrieve season banners and posters
		'''
		# update posters
		database = Tvdb(cache = self.cache, banners = banners)
		try: posters = database[self.tv_show.real_name]['_banners']['season']
		except tvdb_attributenotfound: pass # posters werent loaded so ignore them
		except KeyError: print "No poster for %d : %s" % (self.s_id, self.tv_show.name)
		else: # update posters
			self.poster = [] # clear cached value
			if 'season' in posters: # check for existance
				for entry in posters['season']:
					misc = posters['season'][entry]
					if misc['language'] == 'en' and misc['season'] == str(self.s_id):
						self.poster.append(misc['_bannerpath'])
			# update wide posters
			self.poster_wide = [] # clear ceched value
			if 'seasonwide' in posters: # check for existence
				for entry in posters['seasonwide']:
					misc = posters['seasonwide'][entry]
					if misc['language'] == 'en' and misc['season'] == str(self.s_id):
						self.poster_wide.append(misc['_bannerpath'])

		# update episodes list
		episodes_list = database[self.tv_show.real_name][self.s_id].keys()
		self.episodes = [] # reset cached values
		for i in episodes_list: # generate the episodes list
			new_episode = Episode(e_id = i, s_id = self.s_id, tv_show = self.tv_show, cache=self.cache)
			self.episodes.append(new_episode)

	def toogle_watched(self):
		''' Toogle the watched state '''
		print self.cache
		self.set_watched(not self.watched)
		self.update_watched() # after setting the value call update_watched to propagate change

	def set_watched(self, value):
		''' Set the watched state '''
		self.watched = value
		for episode in self.episodes:
			episode.watched = value
		self.update_watched() # after setting the value call update_watched to propagate change

	def set_torrent(self, torrent):
		'''Set torrent instance associated with this episode'''
		self.torrent=torrent

	def update_watched(self):
		''' Update watched state according to its content'''
		cont = 0
		for episode in self.episodes: # for every episode on this season
			if episode.watched: cont += 1
		if cont == len(self.episodes): self.watched = True
		self.tv_show.update_watched() # call update on tv show

	def get_status(self):
		'''Returns the status this show has, in repect to the user'''
		if self.watched:
			if self.tv_show.status == 'Ended':
				return "completed"
			elif self.tv_show.status == 'Continuing':
				return "watched"
		else: return "unwatched"
# TODO handle episode air date

class Episode:
	'''Class defining a Season Episode

	Its self updatable with method update_info updating episode information
	'''

	def __init__(self, e_id, s_id, tv_show, cache=False):
		'''Constructor method

		Must receive an episode id number, a season id number and a tv_show from where this episode belongs to
		'''
		self.e_id = e_id # 1 based
		self.s_id = s_id # 1 based
		self.name = ''
		self.description = ''
		self.episode_number = ''
		self.director = ''
		self.writer = ''
		self.rating = ''
		self.season = ''
		self.image = ''
		self.imdb_id = ''
		self.airdate = ''
		self.watched = False
		self.torrent = None
		if tv_show: self.tv_show = tv_show # set show instance
		else: raise TVError("tv_show must be a Show instance") # tv_show cant be None
		self.cache=cache
		self.update_info()

	def to_string(self):
		'''Print this class information'''
		print "\t Episode info:\nName: %s\nSeason: %s\nEpisode Number: %s\nDirector: %s\nWriter: %s\nRating: %s\nImage: %s\nAir Date: %s\nIMDB Link: %s" % (self.name, self.season, self.episode_number, self.director, self.writer, self.rating, self.image, self.airdate, self.imdb_id)
		print "Description: %s" % self.description.encode('utf-8') # fix encoding

	def update_info(self):
		'''Searches thetvdb.com and updates all episodes it contains '''
		database = Tvdb(cache = self.cache)
		self.name = database[self.tv_show.real_name][self.s_id][self.e_id]['episodename']
		self.description = database[self.tv_show.real_name][self.s_id][self.e_id]['overview']
		self.episode_number = database[self.tv_show.real_name][self.s_id][self.e_id]['episodenumber']
		self.director = database[self.tv_show.real_name][self.s_id][self.e_id]['director']
		self.writer = database[self.tv_show.real_name][self.s_id][self.e_id]['writer']
		self.rating = database[self.tv_show.real_name][self.s_id][self.e_id]['rating']
		self.season = database[self.tv_show.real_name][self.s_id][self.e_id]['seasonnumber']
		self.image = database[self.tv_show.real_name][self.s_id][self.e_id]['filename']
		imdb_id = database[self.tv_show.real_name][self.s_id][self.e_id]['imdb_id']
		self.imdb_id = IMDB_TITLE + (imdb_id if imdb_id else '')
		self.airdate = database[self.tv_show.real_name][self.s_id][self.e_id]['firstaired']

	def toogle_watched(self):
		''' Toogle the watched state '''
		self.set_watched(not self.watched)
		self.update_watched() # after setting the value call update_watched to propagate change

	def set_watched(self, value):
		''' Set the watched state '''
		self.watched = value
		self.update_watched() # after setting the value call update_watched to propagate change

	def set_torrent(self, torrent):
		'''Set torrent instance associated with this episode'''
		self.torrent=torrent

	def update_watched(self):
		''' Update watched state according to its content'''
		# call update on the belonging season
		self.tv_show.seasons[self.s_id-1].update_watched()

	def already_aired(self):
		'''Returns bollean if this this episode has aired or not'''
		if self.airdate == None: return False
		date_split = self.airdate.split('-')
		return datetime.date.today() > datetime.date(int(date_split[0]),int(date_split[1]),int(date_split[2]))

	def get_status(self):
		'''Returns the status this show has, in repect to the user'''
		if self.watched:
			if self.tv_show.status == 'Ended':
				return "completed"
			elif self.tv_show.status == 'Continuing':
				return "watched"
		else: return "unwatched"
# TODO handle episode air date

# ------------------------------------------------------

if __name__ == '__main__':
	'''Sample Run'''
	name = raw_input('Select a show: ')
	s = Show(name, console = True)
	s.to_string() # print show info
	s.seasons[0].to_string() # print season info
	print "Posters:"
	for a in s.seasons[0].poster: # get list of season posters (use poster_wide for wide posters)
		print a
	s.seasons[0].episodes[0].to_string() # print episode info
