#! /usr/bin/env python

'''
Frontend Aplication for console usage
Latest Update - v1.2
Created - 3.1.16
Copyright (C) 2015 - eximus
'''

USER_STATE_DIR = "user/"

import os, sys
import pickle
from robinit_api import UserContent

def first_use(user_name, path):
	print "Setting things up for first use..."
	if not os.path.exists(USER_STATE_DIR): os.mkdir(USER_STATE_DIR)
	new_user_state = UserContent(user_name)
# Promp user to start adding tv shows or movies
	while (1):
		answer = raw_input("Add Movies or TVShows now? (y/n) ")
		if answer == 'y': break
		elif answer == 'n': return new_user_state
		else: print "Please use \"y\" or \"n\"."
# prompt user to add movies or tv shows
	print "Choose an action:"
	while(1):
		print "1. Add Movies\n2. Add TV Shows\n3. Done"
		try: option = int(raw_input("> "))
		except ValueError: print "Invalid Option"
		if option == 2:
			name = raw_input("Show name: ")
# TODO ADD MULTIPLE MOVIES/SHOWS AT ONCE IN LIST FORM
			new_user_state.add_show(name)
		elif option == 1:
			name = raw_input("Movie name: ")
			new_user_state.add_movie(name)
		elif option == 3: break
		else: print "Invalid Option"
# TODO ....
	new_user_state.save_state(path = "%s%s%s" % (USER_STATE_DIR, user_name, '.dat'))
	return new_user_state

 ### MAIN ###

State = None # will hold the user state

user_name = raw_input("Insert your username: ")
if user_name == "": sys.exit("Invalid username. Exiting...")
# handle data loading or new profile generation
user_state_file = "%s%s%s" % (USER_STATE_DIR, user_name, '.dat')
if not os.path.exists(user_state_file):
	print "No user files in %s. Generating new user" % USER_STATE_DIR
	State = first_use(user_name, user_state_file)
else: # exists then load the previous state
	f = open(USER_STATE_FILE, 'r')
	State = pickle.load(f)

