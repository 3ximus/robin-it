#! /usr/bin/env python

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

'''
Setup user class in first use
Prompt user to add shows or movies to follow
Class state is saved after everything is inserted
'''
def first_use(user_name):
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

'''
Menu for User interaction
'''
def user_interaction(new_user_state):
	while(1):
		# Display Menu
		print "\n\033[1;33;40mChoose an action:\033[0m"
		print "| 1. Add Movies\t\t| 5. Remove Movie"
		print "| 2. Add TV Shows\t| 6. Remove Show"
		print "| 3. List Shows\t\t| 7. Show unwatched"
		print "| 4. List Movies\t| 8. Save and Exit\n"
		try: option = int(raw_input("> "))
		except ValueError:
			print "Invalid Option"
			continue
		if option == 1: # add new movies
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for m in raw_input("Movie name: ").split(','): new_user_state.add_movie(m, verbose = True)
		elif option == 2: # add new shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("Show name: ").split(','): new_user_state.add_show(s, verbose = True)
		elif option == 3: # list shows
			print "\033[3;33mShows:\033[0m"
			new_user_state.shows_to_string()
		elif option == 4: # list movies
			print "\033[3;33mMovies:\033[0m"
			new_user_state.movies_to_string()
		elif option == 5: # remove movies
			pass
		elif option == 6: # remove shows
			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("Show name: ").split(','): new_user_state.remove_show(s, verbose = True)
		elif option == 7: # Mark watched
			u_e = new_user_state.unwatched_episodes()
			for show in u_e:
				print '\033[1;33m' + show + '\033[0m'
				for season in u_e[show]:
					print '  \033[1;36mSeason %s \033[0m' % season
					for ep in u_e[show][season]:
						print '    E: %s - %s' % (ep.episode_number, ep.name)
		elif option == 8:
			new_user_state.save_state(path = USER_STATE_DIR)
			break
		else: print "Invalid Option"
	return new_user_state

# ==========================================
# 	               MAIN
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


