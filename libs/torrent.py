'''
Library containing parser to scrap web pages
Latest Update - v1.1
Created - 28.12.15
Copyright (C) 2015 - eximus
'''
class Torrent():
	'''Torrent data structure'''

	def __init__(self, name = '', link = '', magnet = '', tor_file = '', seeds = '', peers = '', age = '', files = '', size = '', host = ''):
		'''Torrent data Constructor

		Parameters:
			name -- Contains the torrent Name
			link -- Contains the link to the torrent page
			magnet -- Manget link
			tor_file -- partial torrent file link (must be preceded with 'https:' and appended with '.torrent' to be a usable link
			seeds -- Torrent seeds
			peers -- Torrent peers
			age -- Simple representation of torrent age (hours, days, months, years)
			files -- Number of files a torrent contains
			host -- torrent host page (defaults to kickass)
		'''
		self.name = name
		self.link = link
		self.magnet = magnet
		self.tor_file = tor_file
		self.size = size
		self.files = files
		self.age = age
		self.seeds = seeds
		self.peers = peers
		self.host = host

#	def __str__(self):
#		return "name: %s 					\
#					\nlink: %s				\
#					\nmagnet: %s			\
#					\ntorrent file: %s		\
#					\nsize: %s				\
#					\nfiles: %s				\
#					\nage: %s				\
#					\nseeds: %s				\
#					\npeers: %s				\
#					\nhost: %s\n====" % (self.link,
#										self.name,
#										self.magnet,
#										self.tor_file,
#										self.size,
#										self.files,
#										self.age,
#										self.seeds,
#										self.peers,
#										self.host)
