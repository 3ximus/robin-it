#! /usr/bin/env python2

'''
Frontend Aplication for console usage
Latest Update - v1.3
Created - 3.1.16
Copyright (C) 2016 - eximus
'''
__version__ = '1.3'

import os, sys
from robinit_api import UserContent

USER_STATE_DIR = "user/"

def first_use(user_name):
	'''Setup user class in first use

	Prompt user to add shows to follow
	Class state is saved after everything is inserted
	'''
	print "\t\033[3;33mSetting things up for first use...\033[0m"
	if not os.path.exists(USER_STATE_DIR): os.mkdir(USER_STATE_DIR)
	new_user_state = UserContent(user_name)
# Promp user to start adding tv shows
	while (1):
		answer = raw_input("Add Movies or TVShows now? (y/n) ")
		if answer == 'y': break
		elif answer == 'n': return new_user_state
		else: print "Please use \"y\" or \"n\"."
	return user_interaction(new_user_state)

def selection_handler(pseudo_show):
	print "Multiple Results found when building, select one:"
	for i, result in enumerate(pseudo_show.search_results):
		print "%i. %s" % (i, result['seriesname'])
	try: choice = int(raw_input("Selection: "))
	except ValueError: raise # re-raise ValueError
	else:
		if choice < 0 or choice >= len(pseudo_show.search_results): raise ValueError("Invalid option")
	return None

def user_interaction(user_state):
	'''Menu for User interaction'''
	while(1):
		# Display Menu
		print "\n\033[1;33;40mChoose an action:\033[0m"
		print "| 1. Add TV Shows\t| 4. Schedule Download"
		print "| 2. Remove Shows\t| 5. Download Now"
		print "| 3. List Shows\t\t| 6. Save and Exit\n"
		try: option = int(raw_input("> "))
		except ValueError:
			print "Invalid Option"
			continue
		if option == 1: # add new shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("Show name: ").split(','): user_state.add_show(s, selection_handler)
		elif option == 2: # remove shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("Show name: ").split(','): user_state.remove_show(s)
		elif option == 3: # list shows
			print "\033[3;33mShows:\033[0m"
			s = False
			for key in [t for t in user_state.shows if not user_state.shows[t].watched]: # iterate over unwatched shows
				s = True
				print '\t' + key
			if not s: print "\t- No Shows added yet"
		elif option == 4: # schedule downloads
			pass
		elif option == 5: # download now
			pass
		elif option == 6:
			user_state.save_state(path = USER_STATE_DIR)
			break
		else: print "Invalid Option"
	return user_state

# ==========================================
#                  MAIN
# ==========================================

User_State = None # will hold the user state

user_name = raw_input("Insert your username: ")
if user_name == "": sys.exit("Invalid username. Exiting...")
# handle data loading or new profile generation
USER_STATE_FILE = "%srobinit_%s_%s%s" % (USER_STATE_DIR, __version__, user_name, '.pkl') # Only used to look for state file
if not os.path.exists(USER_STATE_FILE): # no previous save file?
	print "No user files in %s. Generating new user \"%s\"" % (USER_STATE_DIR, user_name)
	try: User_State = first_use(user_name) # make new one
	except KeyboardInterrupt: sys.exit('\033[1;33mAborting...\033[0m')
else: # exists then load the previous state
	User_State = UserContent(user_name)
	User_State.load_state(USER_STATE_DIR)
	try: user_interaction(User_State)
	except KeyboardInterrupt: sys.exit('\033[1;33mAborting...\033[0m')

