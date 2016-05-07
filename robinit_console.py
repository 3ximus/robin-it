#! /usr/bin/env python2

'''
Frontend Aplication for console usage
Latest Update - v1.0.1
Created - 3.1.16
Copyright (C) 2016 - eximus
'''
__version__ = '1.0.1'

import os, sys
from colorama import init
from libs.robinit_api import UserContent

init() # make ANSI escape sequences work on windows too

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
	for i, string in enumerate(results):
		print "%i. %s" % (i, string)
	while True:
		try:
			choice = raw_input("Selection: ")
			if choice == 'q': return None
			choice = int(choice)
			if choice < 0 or choice >= len(results): raise ValueError()
			else: break
		except ValueError: print "Please Insert Valid Input"
	return choice

def stat_episode_queue(user_state):
	'''Print stats of episode queue'''
	print "Your List Contains: "
	for key, value in user_state.stat_queue().iteritems():
		print "\t%s -- %s" % (key, value)

def make_queue(user_state):
	'''Function for making user interaction to make an episode queue, gathering torrent information for each one'''

	print "\033[3;33mTo Cancel this process use Ctrl-C at any time\033[0m"
	while True:
		show = user_state.get_show(raw_input("TV Show name: "), selection_handler = selection_handler)
		if not show:
			print "\033[3;31mShow Not Found\033[0m"
			continue
		print "\033[3;32mFound: %s\033[0m\nFor multiple selections separate with ','" % show.name
		try:
# TODO ADD RANGES
			seasons = map(lambda x: int(x) if x!="" else None, raw_input("Season: ").split(','))
			reverse = True if raw_input("Get episodes in reverse order? (y) ") == "y" else False
			episodes = map(lambda x: int(x) if x!="" else None, raw_input("Episodes: ").split(','))
		except ValueError:
			print "Invalid input. Aborting..."
			continue
		user_state.enqueue(user_state.get_episodes_in_range(show=show,
															season_filter=seasons if seasons != [None] else None,
															episode_filter=episodes if episodes != [None] else None,
															reverse=reverse, selection_handler=selection_handler))
		stat_episode_queue(user_state)
		if raw_input("Keep adding? (y) ") != "y":
			break
	print "\n\033[0;33mLinking torrents with episodes...\033[0m"
	failed_ep = []
	counter = 0
	for state, episode, flag in user_state.assign_torrents(user_state.episode_queue,
											force = True if raw_input("Force? (y) ") == "y" else False,
											selection_handler = selection_handler if raw_input("Select individually? (y) ") == "y" else None):
		if not flag: failed_ep.append(episode)
		if not state:
			counter += 1
			print "Gathering: %d/%d -- %s S%02dE%02d%s\r" % (counter, len(user_state.episode_queue),
					episode.tv_show.name, int(episode.s_id), int(episode.e_id)," "*30),
			sys.stdout.flush()
		else:

			print "Gathered: %d/%d -- %s S%02dE%02d -- %s%s" % (counter, len(user_state.episode_queue),
					episode.tv_show.name, int(episode.s_id), int(episode.e_id),
					"\033[0;32mSucess\033[0m" if flag else "\033[0;31mFailed\033[0m", " "*20)
			sys.stdout.flush()

	print "\rGathered: %d/%d Episodes%s" % (counter - len(failed_ep), len(user_state.episode_queue), " "*40)
	if not failed_ep == []:
		print "\n\033[3;31mFailed to get episodes:\033[0m"
		for ep in failed_ep: print "%s S%02dE%02d" % (ep.tv_show.name, int(ep.s_id), int(ep.e_id))
# TODO RETRY ERRORS!!

def download_queue(user_state):
	'''Download torrents of a given episode queues list'''

	print "\033[3;33mTo Cancel this process use Ctrl-C at any time\033[0m"
	counter = 0
	failed_torrents = []
	print "Downloading..."
	for state, torrent, flag in user_state.download_torrents(user_state.episode_queue):
		if torrent == None and state:
			print "Failed torrent: %d/%d" % (counter, len(user_state.episode_queue)) # TODO FIX THIS
			continue
		if not state:
			counter += 1
			print "Downloading: %d/%d -- %s\r" % (counter, len(user_state.episode_queue), torrent.name[:40]),
			sys.stdout.flush()
		else:
			if not flag: failed_torrents.append(torrent)
			print "Downloaded: %d/%d -- %s -- %s%s" % (counter, len(user_state.episode_queue), torrent.name[:40],
					"\033[0;32mSucess\033[0m" if flag else "\033[0;31mFailed\033[0m", " "*15)
			sys.stdout.flush()
	print "\nDownloaded: %d/%d Torrents%s" % (counter - len(failed_torrents), len(user_state.episode_queue), " "*80)

def user_interaction(user_state):
	'''Menu for User interaction'''

	while True:
		# Display Menu
		print "\n\033[1;33;40mChoose an action:\033[0m"
		print "| 1. Add TV Shows\t| 5. Build Queue"
		print "| 2. Remove Shows\t| 6. Download Now (Uses Queue)"
		print "| 3. List Shows\t\t| 7. Schedule Download"
		print "| 4. View Queue\t\t| 8. Save and Exit\n"

		try: option = int(raw_input("> "))
		except ValueError:
			print "Invalid Option"
			continue
		if option == 1: # add new shows
			'''Allows user to add multiple shows'''

			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("TV Show name: ").split(','):
				state = user_state.add_show(s, selection_handler = selection_handler)
				if state: print "\033[32mShow added:\033[0m %s" % state
				elif state == False: print "\033[3;31mShow Not Found\033[0m"
				elif state == None: print "\033[3;33mAborted...\033[0m"

		elif option == 2: # remove shows
			'''Allows user to remove multiple shows'''

			print "\t\033[3;29mseparate names with \',\' for multiple names at once\033[0m"
			for s in raw_input("TV Show name: ").split(','):
				state = user_state.remove_show(s, selection_handler = selection_handler)
				if state: print "\033[31mDeleted Show:\033[0m %s" % state
				elif state == False: print "\033[3;31mShow Not Found\033[0m"
				elif state == None: print "\033[3;33mAborted...\033[0m"

		elif option == 3: # list shows
			'''Displays info of added shows'''

			print "\033[3;33mShows:\033[0m"
			s = False
			for key in user_state.shows:
				s = True
				print '\t' + key
			if not s: print "\t- No Shows added yet"

		elif option == 4: # view queue
			'''Displays info of queued episodes'''

			stat_episode_queue(user_state)

		elif option == 5: # build queue
			'''Prompts user for making or clear the episode queue'''

			if user_state.episode_queue != []:
				stat_episode_queue(user_state)
				if True if raw_input("Clear Queue? (y) ") == "y" else False:
					user_state.clear_queue()
			try: make_queue(user_state)
			except KeyboardInterrupt:
				print "\n\033[3;33mAborted...\033[0m"

		elif option == 6: # download now
			'''Downloads episodes on the queue'''
			stat_episode_queue(user_state)
			try: download_queue(user_state)
			except KeyboardInterrupt:
				print "\n\033[3;33mAborted...\033[0m"

		elif option == 7: # schedule downloads
			print "NOT IMPLEMENTED"

		elif option == 8:
			user_state.save_state(path = USER_STATE_DIR)
			print "Bye"
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

print USER_STATE_FILE

if not os.path.exists(USER_STATE_FILE): # no previous save file?
	print "No user files in %s. Generating new user \"%s\"" % (USER_STATE_DIR, user_name)
	try: User_State = first_use(user_name) # make new one
	except KeyboardInterrupt: sys.exit('\n\033[1;33mAborting...\033[0m')

else: # exists then load the previous state
	User_State = UserContent(user_name)
	User_State.load_state(USER_STATE_DIR)
	try: user_interaction(User_State)
	except KeyboardInterrupt: sys.exit('\n\033[1;33mAborting...\033[0m')

