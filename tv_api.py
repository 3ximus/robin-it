
'''
Api for Getting TV Shows date
Queries http://thetvdb.com/ using  tvdb_api: https://github.com/dbr/tvdb_api
Updates are cached in cache folder
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

from tvdb_api import Tvdb

IMDB_TITLE = "http://www.imdb.com/title/"
CACHE = "cache/"
if not os.path.exists(CACHE): os.mkdir(CACHE)

'''
Class Containing Show information
This class is self updated, once the method update_info is called it updates itself
Tv database is cached to its default location of CACHE
'''
class Show:

# Attributes
	name = '' # tv show name
	description = '' # tv show description
	seasons = [] # seasons
	genre = '' # genre
	runtime = '' # episode times
	status = '' # show status (continuing, stopped)
	network = '' # airing network
	air_dayofweek = '' # week day of hairing
	air_time = '' # hour it airs
	rating = '' # imdb rating
	actors = '' # actors list
	poster = '' # tv show poster
	banner = '' # banner
	imdb_id = '' # imdb id

# Methods
	'''
	Class constructor
	This show will containg the first match in the database
	'''
	def __init__(self, name, watched = False)
			self.name = name # placeholder updated in the update search
			self.watched = watched
			self.update_info()

	'''Make this class printable'''
	def __str__(self):
		return "\t TV Show info:\nName: %s\nGenre: %s\nRuntime: %s\nStatus: %s\nNetwork: %s:\nAiring Day: %s\nAir Time: %s\nRating: %s\nPoster: %s\nIMDB Link: %s\nDescription: %s" % (self.name, self.genre, self.runtime, self.status, self.network, self.air_dayofweek, self.air_time, self.rating, self.poster, self.imdb_id, self.description)

	'''
	Searches thetvdb.com and updates class attributes
	If cache is False, update from the database is forced
	'''
	def update_info(self, cache = CACHE):
		database = Tvdb(cache = cache)
		self.name = database[self.name]['seriesname'] # update tv show name
		seasons_list = database[self.name] # retrieve list of available seasons

# TODO update TV Show info

# TODO update seasons list generating the correct instances of Season so they can be self updatable
		sc = 0
		for season in self.seasons:
			if season.watched: sc+=1 # increment number of watched seasons
			season.update_info() # update each season
		if sc == len(self.seasons): # verify if we watched all the seasons
			self.watched = True

	''' Toogle the watched state '''
	def toogle_watched(self):
		self.watched = not self.watched # toogle watched
		for season in self.seasons: # replicate action to every season
			season.set_watched(self.watched)
			

'''
Class defining a TV Show Season
Its is self updatable with method update_info, this updates every episode information
Update function generates cache on CACHE directory by default
'''
class Season(list):

#Attributes
	s_id = 0 # season numeric id
	tv_show = None # Show instance
	poster = [] # list of season poster
	poster_wide = [] # list of season wide posters
	episodes = 0 # number of episodes

# Methods
	def __init__(self, s_id, tv_show, watched = False):
		self.s_id = s_id
		if tv_show: self.tv_show = tv_show
		else raise ValueError("No Tv Show assigned")
		self.watched = watched
	
	'''Make this class printable'''
	def __str__(self):
		for episode in self: return_string = return_string = episode.__str__()
		return return_string

	'''
	Searches thetvdb.com and updates all episodes it contains
	If cache is False, update from the database is forced
	'''
	def update_info(self, cache = CACHE):
		# update posters
		database = Tvdb(cache = cache, banners = True)
		posters = database[self.tv_show.name]['_banners']['season']:
		for entry in posters['season']: # update posters
			misc = posters['season'][entry]
			if misc['language'] == 'en' and misc['season'] == str(s_id):
				self.poster.append(misc['_bannerpath'])

		for entry in posters['seasonwide']: # update wide posters
			misc = posters['seasonwide'][entry]
			if misc['language'] == 'en' and misc['season'] == str(s_id):
				self.poster_wide.append(misc['_bannerpath'])

		self.episodes = len(self)
		for episode in self:
			episode.update_info() # TODO verify if episode its the reference to this list element or just a copy

	''' Toogle the watched state '''
	def toogle_watched(self, value):
		pass
	
	''' Set the watched state '''
	def set_watched(self, value):
		self.watched = value
		for episode in self:
			
	
'''
Class defining a Season Episode
Its is self updatable with method update_info updating episode information
Update function generates cache on CACHE directory by default
'''
class Episode:

# Attributes
	name = ''
	description = ''
	episode_number = ''
	director = ''
	rating = ''
	season = ''
	image = ''
	imdb_id = ''
	airdate = ''
	watched = False

# Methods
	def __init(self, watched = False):
		self.watched = watched

	'''Make this class printable'''
	def __str__(self):
		return "<Episode %s - %s>" % (ep_id, name)

	def update_info(self):
		pass

