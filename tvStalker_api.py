#! /usr/bin/env python

'''
Api for traking tvShows
user state is persistent across runs
Created - 29.12.15
Copyright (C) 2015 - eximus
'''

import tvdb_api
import cPickle

USER_STATE_PATH = "" # TODO

'''
This class Contains all user information
The class state is saved to a file frequently and at the end os usage
Class state is also loaded at the begining of the program
'''
class _user_content:
	def __init__(self):
		self.following = []
		self.watched = []

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
Class Containing Show information
'''
class Show:
	def __init__(self):
		self.seasons = []
		self.watched = False
	def __str__(self):
		return "" # TODO
	def update_info(self):
		pass

'''
Class defining a TV Show Season
'''
class Season:
	def __init__(self, s_id):
		self.s_id = s_id
		self.episodes = []
		self.watched = False
	def __str__(self):
		return "<Season %s>" % s_id
	def update_info(self):
		pass

'''
Class defining a Season Episode
'''
class Episode:
	def __init(self, ep_id, name):
		self.ep_id = ep_id
		self.name = name
		self.watched = False
		self.lenght = 0
	def __str__(self):
		return "<Episode %s - %s>" % (ep_id, name)
	def update_info(self):
		pass



