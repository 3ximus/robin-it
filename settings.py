'''
Holds global variables
Latest Update - v1.0
Created - 29.10.16
Copyright (C) 2016 - eximus
'''

__version__ = '1.0'
from libs.config import Config

def init(): # call only once to prevent multiple initialization
	'''Initializer global variables'''
	global config
	config = Config

	global _DEFAULTS
	_DEFAULTS =  {
		'torrents': {
			'piratebay_allow':True,
			'kickass_allow':False,
			'rarbg_allow':False,
			'piratebay':"https://pirateproxy.vip",
			'rarbg':"https://rarbg.to",
			'kickass':"http://kickasstorrents.to"
		},
		'subtitles': {
			'sub_en':True,
			'sub_pt':True
		},
		'directories':{
			'storage_dir':'./storage',
			'cache_dir':'./cache',
			'user_dir':'./user'
		},
		'definition':{
			'sd':False,
			'hd720':True,
			'hd1080':False
		},
		'other':{
			'update_show_interval':10
		}
	}

	global _CONFIG_FILE
	_CONFIG_FILE = 'config'

	global _TVDB_BANNER_PREFIX, _TVDB_API_KEY
	_TVDB_BANNER_PREFIX = "http://thetvdb.com/banners/"
	_TVDB_API_KEY = "750B91D6C4BD0717"

	global _USER_AGENT_HEADER
	_USER_AGENT_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}

	global _RESULTS_TIMEOUT
	_RESULTS_TIMEOUT = 20

	global _MAIN_COLOR, _RED_COLOR, _GREEN_COLOR, _MAIN_COLOR_RGB_ALPHA
	_MAIN_COLOR = "#323841"
	_RED_COLOR = "#bf273d"
	_GREEN_COLOR = "#03a662"
	_MAIN_COLOR_RGB_ALPHA = "rgba(50,56,65,230)"

	global _BLUR_RADIOUS, _DARKNESS
	_BLUR_RADIOUS = 10
	_DARKNESS = 0.6

	global _SEASON_MAX_COL, _EPISODE_MAX_COL
	_SEASON_MAX_COL = 5
	_EPISODE_MAX_COL = 3

	global _MAX_UPDATE_SHOW_INTERVAL
	_MAX_UPDATE_SHOW_INTERVAL = 45