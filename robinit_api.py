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

class UserContent:
	'''User TV Shows Content Class

	This class contains all user content
	Contains list with following shows being Show instances
	'''

	def __init__(self, uname = '', empty = False):
		if not empty:
			if uname != '': self.user_name = uname
			else: raise ValueError("Username cannot be empty")
		else: self.user_name = ''
		self.tvdb_apikey = '' # TODO API KEY
		# tv shows
		self.shows = {} # following tv shows

# ==========================================
# 	          GENERIC METHODS
# ==========================================

	def save_state(self, path = None, fd = None):
		'''Saves the current class state to a file

		This method closes the file if given
		'''
		if path:
			path = "%srobinit_%s_%s%s" % (path, __version__, self.user_name, '.pkl')
			fd = open(path, 'wb')
		if not fd: raise ValueError("No path or file passed to save method")
		cPickle.dump(self.__dict__, fd, cPickle.HIGHEST_PROTOCOL)
		fd.close()

	def load_state(self, path = None, fd = None):
		'''Loads the current class state from a file

		This method closes the file if given
		'''
		if path:
			path = "%srobinit_%s_%s%s" % (path, __version__, self.user_name, '.pkl')
			fd = open(path, 'rb')
		if not fd: raise ValueError("No path or file passed to load method")
		tmp_dict = cPickle.load(fd)
		fd.close()
		self.__dict__.update(tmp_dict)

	def find_item(self, name, given_list):
		'''Find a key in a dictionry using a partial name

		Basicly search for the correct name
		For multiple matches promp user to choose from found results
		Returns correct key name
		'''
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

	def force_update(self, name = None):
		'''Force update

		This is a generator function, so you to run it you must iterate over it, it will yieald the name of the show being update each time
		If name is not given the where parameter is used to update everything in that category,
			if where is not given either everything will be updated by default
		Note: this may take a long time because it updates all the information contained
		'''
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
		else: raise ValueError("Where parameter in force update not accepatble")

# ==========================================
# 	             TV SHOWS
# ==========================================

	def add_show(self, name, verbose = True, selection_handler = None):
		'''Add TV SHOW to the follwed tvshows dictionary

		Parameters:
			selection_handler -- is a function that must return an integer and receives a partially
				created tv_show instance that contains a variable search_results holding search results
				for given keyword, this function must then return the user selection.
					NOTE: This argument is mandatory!
			verbose -- will cancel the UnknownTVError excpetion by just printing a message
				to be able to catch it do not use verbose
				verbose will also print a "Show added <show name> message.
		'''
		try: new_show = tv_shows.Show(name)
		except tv_shows.MultipleResultsException:
			i = selection_handler(new_show)
			new_show.build_with_result(i) # use choise to build content
		except tv_shows.UnknownTVError:
			if verbose:
				print "Unknown TV show %s" % name
				return
			else: raise
		self.shows.update({new_show.name:new_show})
		if verbose: print "\033[32mShow added:\033[0m %s" % new_show.name

	def remove_show(self, name, verbose = True):
		'''Remove show by name

		Partial names wil result in displaying multiple results to choose from if conflicts occur
		'''
		show_to_delete = self.find_item(name, self.shows)
		if show_to_delete: # didnt find show
			del(self.shows[show_to_delete])
			if verbose: print "\033[31mDeleted Show:\033[0m %s" % show_to_delete
		else: print "No Show found"

	def toogle_watched_show(self, name = None, item = None):
		'''Toogles watched value

		If an item with watch state is given name is ignored
		If name is given only updates that name otherwise update every show being followed
		This recursivly sets all seasons and episodes to watched/unwatched if its a show
		'''
		if item:
			try: item.toogle_watched() # if valid item
			except AttributeError: raise ValueError("Invalid item passed to toogle_watched_show")
		elif name: # by name
			show = find_item(name, self.shows)
			if show: self.shows[show].toogle_watched()
			else: print "No Show found"
		else: raise ValueError("No parameters passed to toogle_watched_show")

	def update_watched_show(self, name = None):
		'''Forces show watched states to be updated

		If name is given only updates that name otherwise update every show being followed
		Note: This only updates TV Shows
		'''
		if name:
			show = find_item(name, self.shows)
			if show: self.shows[show].update_watched()
			else: print "No Show found"
		else:
			for show in self.shows: self.shows[show].update_watched()

	def unwatched_episodes(self):
		'''Get all episodes unwatched

		Returns a dictionary where keys are shows and the values are lists, these are lists
			of pairs, being the first element the season id and the second a list with instances
			of episode class:
			{ <show_name> : { <season_id> : [ <episode>, <episode>, ... ] , ... }, ... }
		'''
		unwatched_dict = {}
		for show in self.shows:
			if self.shows[show].watched:
				continue
			seasons_dict = self.shows[show].get_unwatched_episodes()
			if seasons_dict != {}:
				unwatched_dict.update({show:seasons_dict})
		return unwatched_dict

	def get_episodes(self, ep_range, reverse = False):
		'''Get Episodes on the given range in form of a list of integers

		This range assumes that all episodes are numbered begining at s01e01
		If reverse is True the range assumes that 0 is the last episode and so on in reverse order
		'''







