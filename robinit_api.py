'''
Api for traking TVShows and Movies
User state is persistent across runs and saved in ./user/ directory
Latest Update - v1.2
Created - 29.12.15
Copyright (C) 2015 - eximus
'''

import cPickle
import tv_shows

'''
User TV Shows Content Class
This class contains all user content
Contains list with following shows being Show instances and watched Shows
Both lists are updated based on the watched variable they contain
'''
class UserContent:

	def __init__(self, uname):
		self.user_name = uname
		self.tvdb_apikey = '' # TODO API KEY
		# tv shows
		self.following_shows = {} # following tv shows
		self.watched_shows = {} # watched tv shows
		# movies
		self.schedule_movies = {} # scheduled movies
		self.watched_movies = {} # watched movies

	'''
	Saves the current class state to a file
	This method closes the file if given
	'''
	def save_state(self, path = None, fd = None):
		if path: fd = open(path + self.user_name + '.pkl', 'wb')
		if not fd: raise ValueError("No path or file passed to save method")
		cPickle.dump(self.__dict__, fd, cPickle.HIGHEST_PROTOCOL)
		fd.close()

	'''
	Loads the current class state from a file
	This method closes the file if given
	'''
	def load_state(self, path = None, fd = None):
		if path: fd = open(path + self.user_name + '.pkl', 'rb')
		if not fd: raise ValueError("No path or file passed to load method")
		tmp_dict = cPickle.load(fd)
		fd.close()
		self.__dict__.update(tmp_dict)


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
			else:
				raise
		self.following_shows.update({new_show.name:new_show})
		if verbose: print "\033[32mShow added:\033[0m %s" % new_show.name

	'''
	Find a key for a tv shows
	Basicly search for the correct name
	For multiple matches promp user to choose from found results
	Returns show name
	'''
	def find_show(self, name, show_list):
		matches = []
		for name_key in show_list: # build match list
			if name.lower() in name_key.lower():
				matches.append(name_key)
		if len(matches) == 0: # no matches found
			return ''
		elif len(matches) == 1:
			return matches[0]
		else: # multiple results, present choice
			print "Multiple results found:"
			for i, s in enumerate(matches): # present matches
				print "%d. %s" % (i, s)
			while(1): # prompt user to choose correct show
				try: choice = int(raw_input("Select: "))
				except ValueError:
					print "Invalid Option"
					continue
				else:
					if choice <= len(matches):
						return matches[choice]
					else:
						print "Invalid Option"
						continue

	'''
	Remove show by name
	Partial names wil result in displaying multiple results to choose from if conflicts occur
	Intended use for verbose is CLI
	'''
	def remove_show(self, name, verbose = False):
		show_to_delete = self.find_show(name, self.following_shows)
		if show_to_delete == '': # didnt find show in following list, try watched list
			show_to_delete = self.find_show(name, self.watched_shows)
		if show_to_delete != '': # didnt find show in following list, try watched list
			del(self.following_shows[show_to_delete])
			if verbose: print "\033[31mDeleted Show:\033[0m %s" % show_to_delete
		else:
			print "No Show found"

	'''
	Toogles watched value for a show
	This recursivly sets all seasons and episodes to watched/unwatched
		and updates following_shows and watched_shows dictionaries
	'''
	def toogle_watched(self, name):
		show_ref = None
		tshow = self.find_show(name, self.following_shows)
		if tshow == '': # didnt find show in following list, try watched list
			tshow = self.find_show(name, self.watched_shows)
			show_ref = self.watched_shows[tshow]
			show_ref.toogle_watched()
			# remove from one list add to the other
			self.following_shows.update({tshow:show_ref})
			del(self.watched_shows[tshow])
		else:
			show_ref = self.following_shows[tshow]
			show_ref.toogle_watched()
			# remove from one list add to the other
			self.watched_shows.update({tshow:show_ref})
			del(self.following_shows[tshow])

	'''
	Forces watched and following tv shows list to be update
	Note: This only updates TV Shows
	'''
	def force_watched_update(self, name):
		pass
# TODO ACTALLY NEEDED ?

	'''
	Force update
	The were paramater show state one of the following 'all', 'shows' or 'movies'
	Updates information of everything
	'''
	def force_update(self, where = 'all'):
		pass

	'''
	Print following shows
	Intended for CLI
	'''
	def shows_to_string(self):
		s = False
		print "Following Shows:"
		for key in self.following_shows:
			s = True
			print '\t' + key
		if not s: print "\t- No Shows added yet"
		s = False
		print "\nWatched Shows:"
		for key in self.watched_shows:
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

