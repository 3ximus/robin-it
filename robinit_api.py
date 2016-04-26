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
	For many functions a selection_handler is needed, in that
		case here is an example of one:

	def selection_handler(results):
		print "Multiple Results found, select one: (Use 'q' to cancel)"
		for i, name in enumerate(results):
			print "%i. %s" % (i, name)
		while(1):
			try:
				choice = raw_input("Selection: ")
				if choice == 'q': return None
				choice = int(choice)
				if choice < 0 or choice >= len(results): raise ValueError()
				else: break
			except ValueError: print "Please Insert Valid Input"
		return choice
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

	def find_item(self, name, selection_handler = None):
		'''Find a key in a dictionary using a partial name returning corerct name

		Parameters:
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See example on constructor Documentation
			name -- keyword to search for
		'''
		matches = []
		for name_key in self.shows: # build match list
			if name.lower() in name_key.lower(): matches.append(name_key)
		if len(matches) == 0: return None # no matches found
		elif len(matches) == 1: return matches[0] # return only match found
		else: # multiple results, present choice
			return matches[selection_handler(matches)]

	def force_update(self, name = None, selection_handler = None):
		'''Force update

		This is a generator function, so to run it you must iterate over it, it will yield the name of the show being updated each time
		Note: this may take a long time because it updates all the information contained
		Parameters:
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See example on constructor Documentation
			name -- if this is not given everything is updated
		'''
		if where == 'shows' or 'all':
			if name: # if name was given
				show = find_item(name, selection_handler = selection_handler)
				if show:
					yield show
					self.shows[show].update_info()
				else: return # show not found
			else:
				for show in self.shows:
					yield show
					self.shows[show].update_info() # update everything
		else: raise ValueError("Where parameter in force update not accepatble")

	def add_show(self, name, selection_handler = None) :
		'''Add TV SHOW to the follwed tvshows dictionary

		Parameters:
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See example on constructor Documentation
			name -- keyword used in search
		'''
		try:
			new_show = tv_shows.Show(name)
			if new_show.search_results != []:
				i = selection_handler(new_show.search_results)
				if i == None: return
				new_show.build_with_result(i) # use choise to build content
		except tv_shows.UnknownTVError:
			print "Unknown TV show %s" % name
			return
		self.shows.update({new_show.name:new_show})
		print "\033[32mShow added:\033[0m %s" % new_show.name

	def remove_show(self, name, verbose = True, selection_handler = None):
		'''Remove show by name

		Partial names wil result in displaying multiple results to choose from if conflicts occur
		Parameters:
			selection_handler -- is a function that must return an integer (or None if canceled) and receives
				a list of strings, this function must then return the user selection.
					NOTE: This argument is mandatory! See example on constructor Documentation
		'''
		show_to_delete = self.find_item(name, selection_handler = selection_handler)
		if show_to_delete: # didnt find show
			del(self.shows[show_to_delete])
			if verbose: print "\033[31mDeleted Show:\033[0m %s" % show_to_delete
		else: print "No Show found"

	def toogle_watched_show(self, name = None, item = None, selection_handler = None):
		'''Toogles watched value

		If an item with watch state is given name is ignored
		If name is given only updates that name otherwise update every show being followed
		This recursivly sets all seasons and episodes to watched/unwatched if its a show
		'''
		if item:
			try: item.toogle_watched() # if valid item
			except AttributeError: raise ValueError("Invalid item passed to toogle_watched_show")
		elif name: # by name
			show = find_item(name, selection_handler = selection_handler)
			if show: self.shows[show].toogle_watched()
			else: print "No Show found"
		else: raise ValueError("No parameters passed to toogle_watched_show")

	def update_watched_show(self, name = None, selection_handler = None):
		'''Forces show watched states to be updated

		If name is given only updates that name otherwise update every show being followed
		Note: This only updates TV Shows
		'''
		if name:
			show = find_item(name, selection_handler = selection_handler)
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







