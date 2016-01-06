#! /usr/bin/env python

'''
Frontend Aplication for console usage
Latest Update - v1.2
Created - 3.1.16
Copyright (C) 2015 - eximus
'''

USER_STATE_DIR = "user/"

import os, sys
import cPickle
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
	while(1):
		print "Choose an action:\n1. Add Movies\n2. Add TV Shows\n3. List already added\n4. Done\n\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
		try: option = int(raw_input("> "))
		except ValueError:
			print "Invalid Option"
			continue
		if option == 2: # add new shows
			for s in raw_input("Show name: ").split(','): new_user_state.add_show(s, verbose = True)
		elif option == 1: # add new movies
			for m in raw_input("Movie name: ").split(','): new_user_state.add_movie(m, verbose = True)
# TODO OPTION 3
		elif option == 3: continue # end insertion loop
		elif option == 4: break # end insertion loop
		else: print "Invalid Option"
# TODO ....
	new_user_state.save_state(path = USER_STATE_DIR)
	return new_user_state

 ### MAIN ###

User_State = None # will hold the user state

user_name = raw_input("Insert your username: ")
if user_name == "": sys.exit("Invalid username. Exiting...")
# handle data loading or new profile generation
user_state_file = USER_STATE_DIR + user_name + '.pkl'
if not os.path.exists(user_state_file):
	print "No user files in %s. Generating new user %s" % (USER_STATE_DIR, user_name)
	User_State = first_use(user_name, user_state_file)
else: # exists then load the previous state
	User_State = UserContent(user_name)
	User_State.load_state(USER_STATE_DIR)

#DUMP USER STATE
print "Dumping..."
for a in User_State.shows:
	print "Name: %s\n\t%s" % (a,User_State.shows[a])
print "End dump..."


