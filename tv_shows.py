'''
API for getting TV Shows information
Queries http://thetvdb.com/ using  tvdb_api: https://github.com/dbr/tvdb_api
Updates are cached in ./cache/ directory
Example usage program in the end
# note that seasons and episodes are indexed with zero base

Latest Update - v1.2
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

from tvdb_api import Tvdb
import os

IMDB_TITLE = "http://www.imdb.com/title/"
CACHE = "cache/"

'''Main Error Class'''
class TVError(Exception):
	pass

'''Unknown tv show error'''
class UnknownTVError(TVError):
	pass

'''Unhandled error'''
class UnhandledTVError(TVError):
	pass

'''
Class Containing Show information
This class is self updated, once the method update_info is called it updates itself
Tv database is cached to its default location of CACHE
'''
class Show:

	'''
	Class constructor
	This show will containg the first match in the database based on the name given
	The console flag should be set to True when running on console mode,
		it is used to prompt the user to choose between one of the available search results
	The graphical flag overrides the console flag and it stops the TV show generation,
		the search_results are stored in self.search_results and should be acessed
		to make the result decision. After that the method build_with_result(int) should be called
		to complete the build process.
	The header only flag only builds the class with Show information and doesn't retrieve seasons
		and episodes info
	'''
	def __init__(self, name, console = True, graphical = False, header_only = False):

		# define class atributes
		self.name = '' # tv show name
		self.description = '' # tv show description
		self.seasons = [] # seasons
		self.genre = '' # genre
		self.runtime = '' # episode times
		self.status = '' # show status (continuing, stopped)
		self.network = '' # airing network
		self.air_dayofweek = '' # week day of hairing
		self.air_time = '' # hour it airs
		self.rating = '' # imdb rating
		self.actors = '' # actors list
		self.poster = '' # tv show poster
		self.banner = '' # banner
		self.imdb_id = '' # imdb id
		self.watched = False
		self.search_results = [] # store search results

		# search for available TV Shows
		self.search_results = Tvdb(cache = CACHE, banners = True).search(name)
		results_amount = len(self.search_results)
		if results_amount == 0: raise UnknownTVError("Unexistent tv_show \"%s\"" % name)
		if not os.path.exists(CACHE): os.mkdir(CACHE) # make directory if unexistent
		if results_amount == 1:
			self.name = self.search_results[0]['seriesname'] # placeholder updated in the update search
			self.update_info(header_only = header_only) # Build class
		else:
			if graphical: return # abort tv show info generation
			elif console:
				try: self._handle_console_results(header_only = header_only)
				except ValueError: raise ValueError("Invalid Option")
			else: raise UnhandledTVError("Multiple search results unhandled")

	'''Print this class information'''
	def to_string(self):
		print "\t TV Show info:\nName: %s\nGenre: %s\nRuntime: %s\nStatus: %s\nNetwork: %s\nAiring Day: %s\nAir Time: %s\nRating: %s\nPoster: %sBanner: %s\nIMDB Link: %s" % (self.name, self.genre, self.runtime, self.status, self.network, self.air_dayofweek, self.air_time, self.rating, self.poster, self.banner, self.imdb_id)
		print "Description: %s" % self.description.encode('utf-8')

	'''
	This handles multiple results in the console
		build_with_result method directly
	'''
	def _handle_console_results(self, header_only = False):
		print "Multiple Results found when building, select one:"
		for i, result in enumerate(self.search_results):
			print "%i. %s" % (i, result['seriesname'])
		try: choice = int(raw_input("Selection: "))
		except ValueError: raise # re-raise ValueError
		else:
			if choice < 0 or choice >= len(self.search_results): raise ValueError("Invalid option")
		self.build_with_result(choice, header_only = header_only) # use choise to build content

	'''
	This function builds class with a given self.search_results index
	Its intended is is to be called by a graphical interface after it checks the
		self.search_results and prompts the user if multiple ones are found and builds with the
		selected option
	'''
	def build_with_result(self, option, header_only = False):
		if option < 0 or option >= len(self.search_results): raise ValueError("Invalid option when generating class")
		self.name = self.search_results[option]['seriesname']
		self.update_info(header_only = header_only) # generate content

	'''
	Searches thetvdb.com and generates class attributes
	This method function is responsible for building the entire data structure of a TV Show
	If cache is False, update from the database is forced
	It is mandatory that self.name is set otherwise build will fail
	'''
	def update_info(self, cache = CACHE, header_only = False):
		if self.name == '': # error check
			raise UnknownTVError("TV Show name not set, build class correctly")

		database = Tvdb(cache = cache)

		if not header_only:
			# updates seasons list
			seasons_list = database[self.name].keys() # retrieve list of available seasons
			if seasons_list[0] == 0: del(seasons_list[0]) # remove first element if it is season 0
			self.seasons = []
			for i in seasons_list: # generates the seasons list
				new_season = Season(s_id = i, tv_show = self)
				self.seasons.append(new_season)

		# update TV Show info
		self.description = database[self.name]['overview']
		self.genre = database[self.name]['genre']
		self.runtime = database[self.name]['runtime']
		self.status = database[self.name]['status']
		self.network = database[self.name]['network']
		self.air_dayofweek = database[self.name]['airs_dayofweek']
		self.air_time = database[self.name]['airs_time']
		self.rating = database[self.name]['rating']
		self.actors = database[self.name]['actors']
		self.poster = database[self.name]['poster']
		self.banner = database[self.name]['banner']
		imdb_id = database[self.name]['imdb_id']
		self.imdb_id = IMDB_TITLE + (imdb_id if imdb_id else '')

		if not header_only: self.update_watched()

	''' Toogle the watched state '''
	def toogle_watched(self):
		self.watched = not self.watched # toogle watched
		for season in self.seasons: # replicate action to every season
			season.set_watched(self.watched)

	'''
	Update watched on the entire tv show
	Propagates decisions to entire show tree
	'''
	def update_watched(self):
		seasons_watched = 0
		for season in self.seasons: # for every season on this show
			episodes_watched = 0
			for episode in season.episodes: # for every episode in this show season
				if episode.watched: episodes_watched += 1
			if episodes_watched == len(season.episodes): # all episodes watched ?
				season.watched = True # if yes season is watched
				seasons_watched += 1
		# all seasons watched then this show is watched
		if seasons_watched == len(self.seasons): self.watched = True

'''
Class defining a TV Show Season
Its self updatable with method update_info, this updates every episode information
Update function generates cache on CACHE directory by default
'''
class Season():

	'''
	Cosntructor method
	Muste receive a season id number and a tv_show from where this season belongs to
	'''
	def __init__(self, s_id, tv_show):
		self.s_id = s_id
		self.episodes = []
		self.poster = [] # list of season poster
		self.poster_wide = [] # list of season wide posters
		self.watched = False
		if tv_show: self.tv_show = tv_show # set show instance
		else: raise TVError("tv_show must be a Show instance") # tv_show cant be None
		self.update_info()

	'''Print this class information'''
	def to_string(self):
		return_string = ''
		for episode in self.episodes: return_string += "%s - %s\n" % (episode.episode_number, episode.name)
		print return_string

	'''
	Searches thetvdb.com and updates all episodes it contains
	If cache is False, update from the database is forced
	'''
	def update_info(self, cache = CACHE):
		# update posters
		database = Tvdb(cache = cache, banners = True)
		try: posters = database[self.tv_show.name]['_banners']['season']
		except KeyError: pass # no posters, so don't update them
		else: # update posters
			self.poster = [] # clear ceched value
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
		episodes_list = database[self.tv_show.name][self.s_id].keys()
		self.episodes = [] # reset cached values
		for i in episodes_list: # generate the episodes list
			new_episode = Episode(e_id = i, s_id = self.s_id, tv_show = self.tv_show)
			self.episodes.append(new_episode)

		self.update_watched()

	''' Toogle the watched state '''
	def toogle_watched(self):
		self.set_watched(not self.watched)

	''' Set the watched state '''
	def set_watched(self, value):
		self.watched = value
		for episode in episodes:
			episode.watched = value
		self.update_watched() # after setting the value call update_watched to propagate change

	''' Update watched state according to its content'''
	def update_watched(self):
		# update watched on tv show this runs on the entire tv show, updating everything
		self.tv_show.update_watched()

'''
Class defining a Season Episode
Its self updatable with method update_info updating episode information
Update function generates cache on CACHE directory by default
'''
class Episode:

	'''
	Cosntructor method
	Muste receive an episode id numeber, a season id number and a tv_show from where this episode belongs to
	'''
	def __init__(self, e_id, s_id, tv_show):
		self.e_id = e_id
		self.s_id = s_id
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
		if tv_show: self.tv_show = tv_show # set show instance
		else: raise TVError("tv_show must be a Show instance") # tv_show cant be None
		self.update_info()

	'''Print this class information'''
	def to_string(self):
		print "\t Episode info:\nName: %s\nSeason: %s\nEpisode Number: %s\nDirector: %s\nWriter: %s\nRating: %s\nImage: %s\nAir Date: %s\nIMDB Link: %s" % (self.name, self.season, self.episode_number, self.director, self.writer, self.rating, self.image, self.airdate, self.imdb_id)
		print "Description: %s" % self.description.encode('utf-8') # fix encoding

	def update_info(self, cache = CACHE):
		database = Tvdb(cache = cache)
		self.name = database[self.tv_show.name][self.s_id][self.e_id]['episodename']
		self.description = database[self.tv_show.name][self.s_id][self.e_id]['overview']
		self.episode_number = database[self.tv_show.name][self.s_id][self.e_id]['episodenumber']
		self.director = database[self.tv_show.name][self.s_id][self.e_id]['director']
		self.writer = database[self.tv_show.name][self.s_id][self.e_id]['writer']
		self.rating = database[self.tv_show.name][self.s_id][self.e_id]['rating']
		self.season = database[self.tv_show.name][self.s_id][self.e_id]['seasonnumber']
		self.image = database[self.tv_show.name][self.s_id][self.e_id]['filename']
		imdb_id = database[self.tv_show.name][self.s_id][self.e_id]['imdb_id']
		self.imdb_id = IMDB_TITLE + (imdb_id if imdb_id else '')
		self.airdate = database[self.tv_show.name][self.s_id][self.e_id]['firstaired']

	''' Toogle the watched state '''
	def toogle_watched(self):
		self.set_watched(not self.watched)

	''' Set the watched state '''
	def set_watched(Self):
		self.watched = value

	''' Update watched state according to its content'''
	def update_watched(self):
		# update watched on tv show this runs on the entire tv show, updating everything
		self.tv_show.update_watched()

''' Example Run '''
if __name__ == '__main__':
	name = raw_input('Select a show: ')
	s = Show(name, console = True)
	s.to_string() # print show info
	s.seasons[0].to_string() # print season info
	print "Posters:"
	for a in s.seasons[0].poster: # get list of season posters (use poster_wide for wide posters)
		print a
	s.seasons[0].episodes[0].to_string() # print episode info
