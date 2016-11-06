

'''
Api for traking TVShows and Movies
User state is persistent across runs and saved in ./user/ directory

Latest Update - v1.0
Created - 29.12.15
Copyright (C) 2016 - eximus
'''
__version__ = '1.0'


import tvshow
import os
import cPickle

# Torrent libs
#from utillib import UtillibError
#import gatherer

class UserContent:
	'''User TV Shows Content Class

	Parameters:
		uname -- username
		cache_dir -- directory used to cache database querie results
		user_dir -- directory used to save the user profile (used to load profile on constructor)

	This class contains all user content
	Contains list with following shows being Show instances
	'''

	def __init__(self, uname = '', cache_dir='cache/', user_dir='user/', storage_dir='storage/', apikey=None):
		if uname != '': self.username = uname
		else: raise ValueError("Username cannot be empty")

		self.tvdb_apikey = apikey
		self.shows = {} # following tv shows
		self.actions = {}

		self.user_dir = user_dir if user_dir else 'user/' # force defaults if None
		self.load_state(self.user_dir)
		self.cache_dir = cache_dir if cache_dir else 'cache/' # force defaults if None
		self.storage_dir = storage_dir if storage_dir else 'cache/' # force defaults if None

# ==========================================
# 	          BASIC METHODS
# ==========================================

	def is_tracked(self, name):
		'''Returns True if show is being tracked, else otherwise'''
		return name in self.shows

	def find_item(self, name):
		'''Find shows in the dictionary using a partial name'''
		matches = []
		for name_key, value in self.shows.iteritems(): # build match list
			if name.lower() in name_key.lower():
				matches.append(value)
		return matches

# SET METHODS
	def set_cache_dir(self, new_dir):
		if not new_dir: return
		self.cache_dir = new_dir
		for t in self.shows.values():
			t.set_cache_dir(new_dir)

	def set_storage_dir(self, new_dir):
		if not new_dir: return
		self.storage_dir = new_dir

	def set_user_dir(self, new_dir):
		if not new_dir: return
		self.user_dir = new_dir

# ==========================================
# 	           MAIN METHODS
# ==========================================

	def save_state(self, path = None, fd = None):
		'''Saves the current class state to a file

		The path argument has predecence over the fd, the latter will be ignored if the former is given
		If no arguments were given the default path from the class will be used (self.user_dir)
		This method closes the file descriptor if given
		'''
		if not os.path.exists(self.user_dir): os.makedirs(self.user_dir)
		if path:
			path = "%s/robinit_%s_%s%s" % (path, __version__.split('.')[0], self.username, '.pkl')
			fd = open(path, 'wb')
		if not fd:
			path = "%s/robinit_%s_%s%s" % (self.user_dir, __version__.split('.')[0], self.username, '.pkl')
			fd = open(path, 'wb')
		cPickle.dump(self.__dict__, fd, cPickle.HIGHEST_PROTOCOL)
		fd.close()

	def load_state(self, path = None, fd = None):
		'''Loads the current class state from a file

		The path argument has predecence over the fd, the latter will be ignored if the former is given
		If no arguments were given the default path from the class will be used (self.user_dir)
		This method closes the file descriptor if given
		'''
		if path:
			path = "%s/robinit_%s_%s%s" % (path, __version__.split('.')[0], self.username, '.pkl')
			try: fd = open(path, 'rb')
			except IOError: return False
		if not fd:
			path = "%s/robinit_%s_%s%s" % (self.user_dir, __version__.split('.')[0], self.username, '.pkl')
			try: fd = open(path, 'rb')
			except IOError: return False
		tmp_dict = cPickle.load(fd)
		fd.close()
		self.__dict__.update(tmp_dict)
		return True

	def add_show(self, name = None, show = None) :
		'''Add TV SHOW to the followed tvshows (self.shows) dictionary

		Parameters:
			name -- show name (this must be the real name otherwise the incorrect show may be loaded)
			show -- show to add

			Returns name of the show added, None if it is already being tracked
		'''
		if show and not self.is_tracked(show.real_name):
			self.shows.update({show.real_name:show})
			return show.real_name
		elif not self.is_tracked(name):
			new_show = tvshow.Show(name, cache=self.cache_dir, apikey=self.tvdb_apikey)
			self.shows.update({new_show.name:new_show})
			return new_show.real_name
		else:
			return None

	def remove_show(self, name):
		'''Remove show by name
			Returns show name if was deleted sucessfully, None if show name is invalid or multiple exist
		'''
		if not self.is_tracked(name): return None
		del(self.shows[name])
		return name

	def toogle_watched(self, name = None, item = None):
		'''Toogles watched value

		If an item with watch state is given name is ignored
		If name is given only updates that name
		This recursivly sets all seasons and episodes to watched/unwatched if its a show/season
		'''
		if item:
			try: item.toogle_watched() # if valid item
			except AttributeError: raise ValueError("Invalid item passed to toogle_watched_show")
		elif name: # by name
			if not self.is_tracked(name):
				raise ValueError("I fucked up somewhere and didnt save the show with the real name")
			else:
				if show: self.shows[show].toogle_watched()

	def unwatched_shows(self):
		'''Get all shows with episodes left to watch'''
		unwatched = []
		for show in self.shows.values():
			if not show.watched :
				for e in reversed(show.get_episodes_list(unaired=False)): # double check ignoring unaired episodes
					if not e.watched:
						unwatched.append(show)
		return unwatched

	def unwatched_episodes(self, name = None, show = None):
		'''Get all episodes unwatched

		Parameters:
			name -- show to get episodes from
			show -- Show instance to get episodes from

			Note:show has precedence over name

		If both parameters are omited it will return episodes from all shows
		Returns a dictionary where keys are shows and the values are lists, these are lists
			of pairs, being the first element the season id and the second a list with instances
			of episode class:
			{ <show_name> : { <season_id> : [ <episode>, <episode>, ... ] , ... }, ... }
		'''
		unwatched_dict = {}

		def _make_unwatched_dict(show):
			if show.watched: return
			if seasons_dict != {}: unwatched_dict.update({show.realname:show.get_unwatched_episodes()})

		if show:
			_make_unwatched_dict(show)
		elif name:
			if self.is_tracked(name):
				_make_unwatched_dict(self.shows[name])
		else:
			for show in self.shows.values():
				_make_unwatched_dict(show)
		return unwatched_dict

	def assign_torrents(self, episode_list, force=False, selection_handler=None):
		'''Assign torrents to every episode given

		Parameters:
			episode_list -- list with episode instances
			force -- force overwrite of torrents if already defined
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See top Documentation
		This function yields every episode it finishes gathering and a flag representing its failure or sucess
		'''
		status = True
		for e in episode_list:
			yield False, e, status
			if not e.torrent or force:
					search_term = '%s %s %s' % (e.tv_show.name, 's%02d' % int(e.s_id) + 'e%02d' % int(e.e_id), "720p")
					try:
						results = gatherer.search(gatherer.KICKASS, search_term)
						if selection_handler:
							choice = selection_handler(gatherer.present_results(results, header=False, output=False))
							if choice:
								e.torrent = results[choice]
								status = True
						else:
							if not results: status = False
							else:
								e.torrent = results[0] # TODO ADD A BETTER METHOD FOR THIS
								status = True
					except UtillibError:
						status = False
			yield True, e, status

