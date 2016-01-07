#! /usr/bin/env python

'''
Frontend Aplication for console usage
Latest Update - v1.2
Created - 3.1.16
Copyright (C) 2015 - eximus
'''

USER_STATE_DIR = "user/"

import os, sys
from robinit_api import UserContent

'''
Setup user class in first use
Prompt user to add shows or movies to follow
Class state is saved after everything is inserted
'''
def first_use(user_name, path):
	print "\t\033[3;33mSetting things up for first use...\033[0m"
	if not os.path.exists(USER_STATE_DIR): os.mkdir(USER_STATE_DIR)
	new_user_state = UserContent(user_name)
# Promp user to start adding tv shows or movies
	while (1):
		answer = raw_input("Add Movies or TVShows now? (y/n) ")
		if answer == 'y': break
		elif answer == 'n': return new_user_state
		else: print "Please use \"y\" or \"n\"."
	return user_interaction(new_user_state)

def user_interaction(new_user_state):
	while(1):
		print "\n\033[1;33;40mChoose an action:\033[0m\n| 1. Add Movies\t\t\t| 4. Remove Movie\n| 2. Add TV Shows\t\t| 5. Remove Show\n| 3. List already added\t\t| 6. Save and Exit\n\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
		try: option = int(raw_input("> "))
		except ValueError:
			print "Invalid Option"
			continue
		if option == 1: # add new movies
			for m in raw_input("Movie name: ").split(','): new_user_state.add_movie(m, verbose = True)
		elif option == 2: # add new shows
			for s in raw_input("Show name: ").split(','): new_user_state.add_show(s, verbose = True)
		elif option == 3:
			print "\033[3;33mShows:\033[0m"
			new_user_state.shows_to_string()
			print "\033[3;33mMovies:\033[0m"
# TODO print movies
		elif option == 4: pass
		elif option == 5: # remove shows
			for s in raw_input("Show name: ").split(','): new_user_state.remove_show(s, verbose = True)
		elif option == 6: break # end insertion loop
		else: print "Invalid Option"
	new_user_state.save_state(path = USER_STATE_DIR)
	return new_user_state


# ==========================================
# 	               MAIN
# ==========================================

User_State = None # will hold the user state

user_name = raw_input("Insert your username: ")
if user_name == "": sys.exit("Invalid username. Exiting...")
# handle data loading or new profile generation
user_state_file = USER_STATE_DIR + user_name + '.pkl'
if not os.path.exists(user_state_file):
	print "No user files in %s. Generating new user \"%s\"" % (USER_STATE_DIR, user_name)
	User_State = first_use(user_name, user_state_file)
else: # exists then load the previous state
	User_State = UserContent(user_name)
	User_State.load_state(USER_STATE_DIR)
	user_interaction(User_State)

#DUMP USER STATE
print "Dumping..."
for a in User_State.following_shows:
	print "Name: %s\n\t%s" % (a,User_State.following_shows[a])
print "End dump..."
#END DUMP USER STATE


