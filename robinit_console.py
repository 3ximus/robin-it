#! /usr/bin/env python2

'''
Frontend Aplication for console usage
Latest Update - v1.3
Created - 3.1.16
Copyright (C) 2016 - eximus
'''
__version__ = '1.3'

import os, sys
from libs.robinit_api import UserContent

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
	return user_interaction(new_user_state)

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
			for s in raw_input("Show name: ").split(','):
				user_state.add_show(s, selection_handler = selection_handler)
		elif option == 2: # remove shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("Show name: ").split(','):
				user_state.remove_show(s, selection_handler = selection_handler)
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
		elif option == 7:
			s = raw_input("Show name: ")
			print user_state.get_episodes_in_range(s, selection_handler = selection_handler)
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

