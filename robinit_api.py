'''
Api for traking TVShows and Movies
User state is persistent across runs and saved in ./user/ directory
Latest Update - v1.3
Created - 29.12.15
Copyright (C) 2015 - eximus
'''
__version__ = '1.3'

import cPickle
import tv_shows

'''
User TV Shows Content Class
This class contains all user content
Contains list with following shows being Show instances
'''
class UserContent:

	def __init__(self, uname = '', empty = False):
		if not empty:
			if uname != '': self.user_name = uname
			else: raise ValueError("Username cannot be empty")
		else: self.user_name = ''
		self.tvdb_apikey = '' # TODO API KEY
		# tv shows
		self.shows = {} # following tv shows
		# movies
		self.movies = {} # scheduled movies

# ==========================================
# 	          GENERIC METHODS
# ==========================================

	'''
	Saves the current class state to a file
	This method closes the file if given
	'''
	def save_state(self, path = None, fd = None):
		if path:
			path = "%srobinit_%s_%s%s" % (path, __version__, self.user_name, '.pkl')
			fd = open(path, 'wb')
		if not fd: raise ValueError("No path or file passed to save method")
		cPickle.dump(self.__dict__, fd, cPickle.HIGHEST_PROTOCOL)
		fd.close()

	'''
	Loads the current class state from a file
	This method closes the file if given
	'''
	def load_state(self, path = None, fd = None):
		if path:
			path = "%srobinit_%s_%s%s" % (path, __version__, self.user_name, '.pkl')
			fd = open(path, 'rb')
		if not fd: raise ValueError("No path or file passed to load method")
		tmp_dict = cPickle.load(fd)
		fd.close()
		self.__dict__.update(tmp_dict)

	'''
	Find a key in a dictionry using a partial name
	Basicly search for the correct name
	For multiple matches promp user to choose from found results
	Returns correct key name
	'''
	def find_item(self, name, given_list):
		matches = []
		for name_key in given_list: # build match list
			if name.lower() in name_key.lower(): matches.append(name_key)
		if len(matches) == 0: return None # no matches found
		elif len(matches) == 1: return matches[0] # return only match found
		else: # multiple results, present choice
			print "Multiple results found:"
			for i, s in enumerate(matches): # present matches
				print "%d. %s" % (i, s)
			while(1): # prompt user to choose correct show
				try: choice = int(raw_input("Select: "))
				except ValueError: print "Invalid Option"
				else:
					if choice < len(matches) and choice >= 0: return matches[choice]
					else: print "Invalid Option"

	'''
	Force update
	This is a generator function, so you to run it you must iterate over it, it will yieald the name of the show being update each time
	The were paramater must be one of the following 'all', 'shows' or 'movies'
	If name is not given the where parameter is used to update everything in that category,
		if where is not given either everything will be updated by default
	Note: this may take a long time because it updates all the information contained
	'''
	def force_update(self, name = None, where = 'all'):
		if where == 'shows' or 'all':
			if name: # if name was given
				show = find_item(name, self.shows)
				if show:
					yield show
					self.shows[show].update_info()
				else: return # show not found
			else:
				for show in self.shows:
					yield show
					self.shows[show].update_info() # update everything
		elif where == 'movies' or where == 'all':
			pass
# TODO MOVIES
		else: raise ValueError("Where parameter in force update not accepatble")

# ==========================================
# 	             TV SHOWS
# ==========================================

	'''
	Add TV SHOW to the follwed tvshows dictionary
	The parameter verbose will cancel the UnknownTVError excpetion by just printing a message
		to be able to catch it do not use verbose
		verbose will also print a "Show added <show name> message.
		Intended use for verbose is CLI
	'''
	def add_show(self, name, verbose = False):
		try: new_show = tv_shows.Show(name, console = True)
		except tv_shows.UnknownTVError:
			if verbose:
				print "Unknown TV show %s" % name
				return
			else: raise
		self.shows.update({new_show.name:new_show})
		if verbose: print "\033[32mShow added:\033[0m %s" % new_show.name

	'''
	Remove show by name
	Partial names wil result in displaying multiple results to choose from if conflicts occur
	Intended use for verbose is CLI
	'''
	def remove_show(self, name, verbose = False):
		show_to_delete = self.find_item(name, self.shows)
		if show_to_delete: # didnt find show
			del(self.shows[show_to_delete])
			if verbose: print "\033[31mDeleted Show:\033[0m %s" % show_to_delete
		else: print "No Show found"

	'''
	Toogles watched value
	If an item with watch state is given name is ignored
	If name is given only updates that name otherwise update every show being followed
	This recursivly sets all seasons and episodes to watched/unwatched if its a show
	'''
	def toogle_watched_show(self, name = None, item = None):
		if item:
			try: item.toogle_watched() # if valid item
			except AttributeError: raise ValueError("Invalid item passed to toogle_watched_show")
		elif name: # by name
			show = find_item(name, self.shows)
			if show: self.shows[show].toogle_watched()
			else: print "No Show found"
		else: raise ValueError("No parameters passed to toogle_watched_show")

	'''
	Forces show watched states to be updated
	If name is given only updates that name otherwise update every show being followed
	Note: This only updates TV Shows
	'''
	def update_watched_show(self, name = None):
		if name:
			show = find_item(name, self.shows)
			if show: self.shows[show].update_watched()
			else: print "No Show found"
		else:
			for show in self.shows: self.shows[show].update_watched()

	'''
	Get all episodes unwatched
	Returns a dictionary where keys are shows and the values are lists, these are lists
		of pairs, being the first element the season id and the second a list with instances
		of episode class:
		{ <show_name> : { <season_id> : [ <episode>, <episode>, ... ] , ... }, ... }
	'''
	def unwatched_episodes(self):
		unwatched_dict = {}
		for show in self.shows:
			if self.shows[show].watched:
				continue
			seasons_dict = {}
			for season in self.shows[show].seasons:
				episodes_list = []
				if not season.watched:
					seasons_dict.update({str(season.s_id):season.episodes})
					continue
				for episode in season.episodes:
					if not episode.watched: episodes_list.append(episode)
				if episodes_list != []: seasons_dict.update({str(season.s_id):episodes_list})
			if seasons_dict != {}: unwatched_dict.update({show:seasons_dict})
		return unwatched_dict

	'''
	Print following shows
	Intended for CLI
	'''
	def shows_to_string(self):
		s = False
		print "Following Shows:"
		for key in [t for t in self.shows if not self.shows[t].watched]: # iterate over unwatched shows
			s = True
			print '\t' + key
		if not s: print "\t- No Shows added yet"
		s = False
		print "\nWatched Shows:"
		for key in [t for t in self.shows if self.shows[t].watched]: # iterate over watched shows
			s = True
			print '\t' + key
		if not s: print "\t- No Shows watched yet"

# ==========================================
# 	             MOVIES
# ==========================================

	def add_movie(self, name, verbose = False):
		#self.movies.update()
		pass

	def remove_movie(self, name):
		pass

	'''
	Print scheduled movies
	Intended for CLI
	'''
	def movies_to_string(self):
		s = False
		print "Scheduled Movies:"
		for key in [t for t in self.movies if not self.movies[t].watched]: # iterate over unwatched shows
			s = True
			print '\t' + key
		if not s: print "\t- No Movies added yet"
		s = False
		print "\nWatched Shows:"
		for key in [t for t in self.movies if self.movies[t].watched]: # iterate over watched shows
			s = True
			print '\t' + key
		if not s: print "\t- No Movies watched yet"




