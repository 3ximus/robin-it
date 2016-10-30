

'''
Api for traking TVShows and Movies
User state is persistent across runs and saved in ./user/ directory

Latest Update - v0.6
Created - 29.12.15
Copyright (C) 2016 - eximus
'''
__version__ = '0.6'


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

	def __init__(self, uname = '', cache_dir='cache/', user_dir='user/', storage_dir='storage/'):
		if uname != '': self.username = uname
		else: raise ValueError("Username cannot be empty")

		self.tvdb_apikey = '' # TODO API KEY
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
		# TODO remove this if no problem has come up
		#if self.find_item(name): return True
		#return False

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
		if not os.path.exists(self.user_dir): os.mkdir(self.user_dir)
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

	def find_item(self, name):
		'''Find a key in a dictionary using a partial name returning correct name '''
		matches = []
		for name_key in self.shows: # build match list
			if name.lower() in name_key.lower():
				matches.append(name_key)
		if len(matches) == 0: return None # no matches found
		elif len(matches) == 1: return matches[0] # return only match found
		else: return matches

	def force_update(self, name = None, selection_handler = None): # TODO marked for review
		'''Force update

		This is a generator function, so to run it you must iterate over it, it will yield the name
			of the show being updated each time
		Note: this may take a long time because it updates all the information contained
		Parameters:
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See top Documentation
			name -- if this is not given everything is updated
		'''
		if name: # if name was given
			show = self.find_item(name, selection_handler = selection_handler)
			if show:
				yield show
				self.shows[show].update_info()
			else: return # show not found
		else:
			for show in self.shows:
				yield show
				self.shows[show].update_info() # update everything

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
			new_show = tvshow.Show(name, cache=self.cache_dir)
			self.shows.update({new_show.name:new_show})
			return new_show.real_name
		else:
			return None


	def remove_show(self, name):
		'''Remove show by name
			Returns show name if was deleted sucessfully, None if show name is invalid or multiple exist
		'''
		show_to_delete = self.find_item(name)
		if not show_to_delete or type(show_to_delete) == list: return None

		del(self.shows[show_to_delete])
		return show_to_delete

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
			show = self.find_item(name)
			if type(show) == list: raise ValueError("I fucked up somewhere and didnt save the show with the real name")
			if show: self.shows[show].toogle_watched()

	def mark_watched_until(self, name = None, season = None, episode = None, item = None, selection_handler = None):
		'''Mark episodes/seasons watched until the episode/season given'''
# TODO
		pass

	def update_watched_show(self, name = None, selection_handler = None): # TODO marked for review
		'''Forces show watched states to be updated

		If name is given only updates that name otherwise update every show being followed
		Note: This only updates TV Shows
		'''
		if name:
			show = self.get_show(name, selection_handler = selection_handler)
			if show: show.update_watched()
			else: print "No Show found"
		else:
			for show in self.shows: self.shows[show].update_watched()

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
		if show:
			pass # TODO get episodes from given show
		if name:
			pass # TODO get episodes from given show
		for show in self.shows:
			if self.shows[show].watched:
				continue
			seasons_dict = self.shows[show].get_unwatched_episodes()
			if seasons_dict != {}:
				unwatched_dict.update({show:seasons_dict})
		return unwatched_dict

	def get_episodes_in_range(self, name = None, show = None, season_filter = None, episode_filter = None, reverse = False, selection_handler = None):
		'''Get Episodes with a given season or episode filter

		Parameters:
			name -- name of show to select
			show -- show to select
			season_filter -- list of seasons
			episode_filter -- list of episodes. This will be applied after the season filter so any range given here
								will be applied after unwanted seasons are removed.
			reverse -- if True the range assumes that 0 is the last episode aired and so on in reverse order
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See top Documentation
		'''
		if not show: show = self.get_show(name, selection_handler = selection_handler)
		if not show: return None
		aired_list = [ep for ep in show.get_episodes_list() if ep.already_aired()]
		if reverse: aired_list = list(reversed(aired_list))
		if season_filter: aired_list = filter(lambda x: x.s_id in season_filter, aired_list)
		if episode_filter: aired_list = filter(lambda x: aired_list.index(x) in map(lambda x: x-1,episode_filter), aired_list)
		return aired_list

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

