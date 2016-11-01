'''
Holds global variables
Latest Update - v0.6
Created - 29.10.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.6'
from libs.config import Config

def init():
	'''Initializer global variables'''
	global config
	config = Config

	global _DEFAULTS
	_DEFAULTS =  {'torrents': {'kickass_allow':True,
							'rarbg_allow':False,
							'piratebay_allow':False},
				'subtitles': {'sub_en':True,
							'sub_pt':True},
				'directories':{ 'storage_dir':'./storage',
								'cache_dir':'./cache',
								'user_dir':'./user'},
				'other':{'definition':'hd'}}

	global _CONFIG_FILE
	_CONFIG_FILE = 'config'

	global _TVDB_BANNER_PREFIX
	_TVDB_BANNER_PREFIX = "http://thetvdb.com/banners/"

	global _RESULTS_TIMEOUT
	_RESULTS_TIMEOUT = 20

	global _MAIN_COLOR, _RED_COLOR, _GREEN_COLOR
	_MAIN_COLOR = "#323841"
	_RED_COLOR = "#bf273d"
	_GREEN_COLOR = "#03a662"

	global _BLUR_RADIOUS, _DARKNESS
	_BLUR_RADIOUS = 10
	_DARKNESS = 0.6

	global _SEASON_MAX_COL, _EPISODE_MAX_COL
	_SEASON_MAX_COL = 5
	_EPISODE_MAX_COL = 3

	global _UPDATE_SHOW_INTERVAL
	_UPDATE_SHOW_INTERVAL = 10