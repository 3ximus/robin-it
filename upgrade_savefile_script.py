#! /usr/bin/env python

'''
This script tries to update file from older versions to newer versions
Latest Update - v1.3
Created - 7.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '1.3'

import tv_shows, os
from robinit_api import UserContent

USER_STATE_DIR = "user/"

user_name = raw_input('user_name: ')
retrieved_state = UserContent(user_name)
retrieved_state.load_state(USER_STATE_DIR)
# --
upgraded_uState = UserContent(user_name)
upgraded_uState.shows = retrieved_state.shows
upgraded_uState.movies = retrieved_state.movies
upgraded_uState.tvdb_apikey = retrieved_state.tvdb_apikey
filename = raw_input('save file name (if name is %srobinit_%s_%s%s leave blank): ' % (USER_STATE_DIR, __version__, user_name, '.pkl'))
if filename == '': filename = "%srobinit_%s_%s%s" % (USER_STATE_DIR, __version__, user_name, '.pkl')
os.remove(filename)
upgraded_uState.save_state(path = USER_STATE_DIR)
print "Savefile sucessfully upgraded!"

