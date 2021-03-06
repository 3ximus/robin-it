

'''
Api for traking TVShows and Movies
User state is persistent across runs and saved in ./user/ directory

Latest Update - v1.0
Created - 29.12.15
Copyright (C) 2016 - eximus
'''
__version__ = '1.0'


from libs.tvshow import Show, Episode
import os
import cPickle

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
		self.pending_download = {}
		self.scheduled = {} # for scheduled episodes
		self.scheduled_shows = {} # for scheduled shows

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

	def find_item(self, name, lst=None, key=None, return_key=False):
		'''Find shows in the dictionary using a partial name

		Optional Parameters
			lst -- list where to search for, if omitted self.shows is used (this can only be a dictionary)
			key -- one argument function to specify the field used in comparisons,
					similar to the ones used in builtin map function or list.sort()
			return_key -- if set to true the returned list will contain both the keys and value of the matched
					element in the dictionary
		'''
		matches = []
		search_in = self.shows.iteritems() if lst == None else lst.iteritems()
		for name_key, value in search_in: # build match list
			k = name_key if key == None else key(name_key) # apply filter if needed
			if name.lower() in k.lower():
				matches.append((name_key,value) if return_key else value)
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
			new_show = Show(name, cache=self.cache_dir, apikey=self.tvdb_apikey)
			self.shows.update({new_show.real_name:new_show})
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

	def unwatched_shows(self):
		'''Get all shows with episodes left to watch'''
		unwatched = []
		for show in self.shows.values():
			if not show.watched :
				for e in reversed(show.get_episodes_list(unaired=False)): # double check ignoring unaired episodes
					if not e.watched:
						unwatched.append(show)
		return unwatched

	def schedule(self, item):
		'''Adds an item to the scheduled list, this item can only be a Show or an Episode'''
		if isinstance(item, Episode):
			self.scheduled.update({item.tv_show.real_name:item})
		elif isinstance(item, Show):
			self.scheduled_shows.update({item.real_name: item})

	def pend_download(self, item, torrent_list):
		'''Adds an item to the pending download list'''
		if isinstance(item, Episode):
			self.pending_download.update({item:torrent_list})

	def remove_pending(self, item):
		del(self.pending_download[item])

