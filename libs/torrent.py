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

	def __str__(self):
		print "name: %s" % self.name
		print "link: %s" % self.link
		print "magnet: %s" % self.magnet
		print "torrent file: %s" % self.tor_file
		print "size: %s" % self.size
		print "files: %s" % self.files
		print "age: %s" % self.age
		print "seeds: %s" % self.seeds
		print "peers: %s" % self.peers
		print "host: %s" % self.host
		print " ==== "
