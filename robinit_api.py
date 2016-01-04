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
	user_name = ''
	shows = None
	movies = None

	def __init__(self, uname):
		self.user_name = uname

	'''Defines the pickling behavior when save state is called'''
	def __getstate__(self):
		pass

	'''Defines the unpickling behavior when load state is called'''
	def __setstate__(self, dict):
		pass

	'''Saves the current class state to a file'''
	def save_state(self, path = None, fd = None):
		pass

	'''Loads the current class state to a file'''
	def load_state(self, path = None, fd = None):
		pass

	def add_show(self, name):
		pass

	def remove_show(self, name):
		pass

	def add_movie(self, name):
		pass

	def remove_movie(self, name):
		pass

'''
This class tv show information
The class state is saved to a file frequently and at the end os usage
Class state is also loaded at the begining of the program
'''
class _tv_user_content:
# Attributes
	following = []
# Methods
	def __init__(self):
		pass

	'''Add a new show to the following list'''
	def add_show(self, show):
		pass

	'''Remove show from following list'''
	def remove_show(self, show):
		pass

	'''Updates entire library'''
	def _update(self):
		pass


'''
This class Contains all user information
The class state is saved to a file frequently and at the end os usage
Class state is also loaded at the begining of the program
'''
class _movie_user_content:
	pass

