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
Wrapper class for all user interaction and data handling
'''
class UserContent:

	def __init__(self, uname):
		self.user_name = uname
		self.shows = {}
		self.movies = {}

	'''
	Saves the current class state to a file
	This method closes the file if given
	'''
	def save_state(self, path = None, fd = None):
		if path: fd = open(path + self.user_name + '.pkl', 'wb')
		if not fd: raise ValueError("No path or file passed to save method")
		cPickle.dump(self.__dict__, fd, cPickle.HIGHEST_PROTOCOL)
		fd.close()

	'''Loads the current class state from a file'''
	def load_state(self, path = None, fd = None):
		if path: fd = open(path + self.user_name + '.pkl', 'rb')
		if not fd: raise ValueError("No path or file passed to load method")
		tmp_dict = cPickle.load(fd)
		fd.close()
		self.__dict__.update(tmp_dict)

	'''
	----
	verbose will cancel the unknown tv show excpetion by just printing a message

	'''
	def add_show(self, name, verbose = False):
		try: new_show = tv_shows.Show(name, console = True)
		except tv_shows.UnknownTVError:
			if verbose:
				print "Unknown TV show %s" % name
				return
			else:
				raise
		self.shows.update({new_show.name:new_show})
		if verbose: print "Show added %s" % new_show.name

	def remove_show(self, name):
		del(shows[name])
		

	def add_movie(self, name, verbose = False):
		#self.movies.update()
		pass

	def remove_movie(self, name):
		pass

