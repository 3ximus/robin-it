#! /usr/bin/env python

'''
Api for traking TVShows and Movies
User state is persistent across runs
Latest Update - v1.2
Created - 29.12.15
Copyright (C) 2015 - eximus
'''

import cPickle

USER_STATE_PATH = "" # TODO


'''
Wrapper class for all user interaction and data handling
'''
class UserContent:
	name = ''
	def __init__(self, name):
		self.name = name

	'''Defines the pickling behavior when save state is called'''
	def __getstate__(self):
		pass

	'''Defines the unpickling behavior when load state is called'''
	def __setstate__(self, dict):
		pass

	'''Saves the current class state to a file'''
	def save_state(self, path):
		pass

	'''Loads the current class state to a file'''
	def load_state(self, path):
		pass

'''
This class Contains all user information
The class state is saved to a file frequently and at the end os usage
Class state is also loaded at the begining of the program
'''
class _movie_user_content:
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



