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
	while True:
		try:
			choice = raw_input("Selection: ")
			if choice == 'q': return None
			choice = int(choice)
			if choice < 0 or choice >= len(results): raise ValueError()
			else: break
		except ValueError: print "Please Insert Valid Input"
	return choice

def download_episodes(user_state, episode_list):
	user_state.assign_torrents(episode_list, force = True if raw_input("Force? (y) ") == "y" else False)
	print "Downloading..."
	pass

def user_interaction(user_state):
	'''Menu for User interaction'''
	while True:
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
			for s in raw_input("TV Show name: ").split(','):
				state = user_state.add_show(s, selection_handler = selection_handler)
				if state: print "\033[32mShow added:\033[0m %s" % state
				elif state == False: print "\033[3;31mShow Not Found\033[0m"
				elif state == None: print "\033[3;33mAborted...\033[0m"
		elif option == 2: # remove shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("TV Show name: ").split(','):
				state = user_state.remove_show(s, selection_handler = selection_handler)
				if state: print "\033[31mDeleted Show:\033[0m %s" % state
				elif state == False: print "\033[3;31mShow Not Found\033[0m"
				elif state == None: print "\033[3;33mAborted...\033[0m"
		elif option == 3: # list shows
			print "\033[3;33mShows:\033[0m"
			s = False
			for key in user_state.shows:
				s = True
				print '\t' + key
			if not s: print "\t- No Shows added yet"
		elif option == 4: # schedule downloads
			print "NOT IMPLEMENTED"
		elif option == 5: # download now
# TODO MAKE THIS GLOBAL?
			episode_list = []
			while True:
				show = user_state.get_show(raw_input("TV Show name: "), selection_handler = selection_handler)
				if not show:
					print "\033[3;31mShow Not Found\033[0m"
					continue
				print "\033[3;32mFound: %s\033[0m\nFor multiple selections separate with ','" % show.name
				try:
# TODO ADD RANGES
					seasons = map(lambda x: int(x) if x!="" else None, raw_input("Season: ").split(',')) # convert input to list of integers
					reverse = True if raw_input("Get episodes in reverse order? (y) ") == "y" else False
					episodes = map(lambda x: int(x) if x!="" else None, raw_input("Episodes: ").split(',')) # convert input to list of integers
				except ValueError:
					print "Invalid input. Aborting..."
					continue
				episode_list.extend(user_state.get_episodes_in_range(show=show,
																	season_filter=seasons if seasons != [None] else None,
																	episode_filter=episodes if episodes != [None] else None,
																	reverse=reverse,
																	selection_handler=selection_handler))
				stats = {}
				for item in episode_list:
					stats[item.tv_show.name] = 1 if item.tv_show.name not in stats else stats[item.tv_show.name]+1
				print "Your List Contains: "
				for key, value in stats.iteritems():
					print "\t%s -- %s" % (key, value)
				if raw_input("Keep adding? (y) ") != "y":
					download_episodes(user_state, episode_list)
					break
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

