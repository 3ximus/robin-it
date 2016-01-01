'''
Library containing parser to scrap web pages
Latest Update - v1.1
Created - 28.12.15
Copyright (C) 2015 - eximus
'''
import re
from sgmllib import SGMLParser
from bs4 import BeautifulSoup

KICKASS = "http://kickass.unblocked.la/"

'''
Torrent data structure
'''
class Torrent():
	'''
	Note that all items in the constructor are strings
	name : Contains the torrent Name
	link : Contains the link to the torrent page
	magnet : Manget link
	tor_file : partial torrent file link
				(must be preceded with 'https:' and appended with '.torrent' to be a usable link
	seeds = Torrent seeds
	peers = Torrent peers
	age = Simple representation of torrent age (hours, days, months, years)
	files = Number of files a torrent contains
	host = torrent host page (defaults to kickass)
	'''
	def __init__(self, name = '', link = '', magnet = '', tor_file = '', seeds = '', peers = '', age = '', files = '', size = '', host = KICKASS):
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


'''
Beautiful Soup 4 Custom parser
Parser class derivation of BeautifulSoup4
Returns a tuple with Torrent class instances
'''
class BS4():
	def __init__(self):
		self.parsed = []
		self.btree = None # not an actual btree but a 'beautiful tree'

	'''
	Callable feed method
	Receives the content to parse, or the open filedescriptor and how to parse it
	'''
	def feed(self, html, parse_for='torrent'):
		self.btree = BeautifulSoup(html, "lxml") # parse the webpage with lxml parser
		if parse_for == 'torrent': self._torrent_parsing(host = KICKASS) # TODO pass another host if needed
		else: raise ValueError("Unknown parser option given")

	''' Prepare for parsing according to host structure '''
	def _torrent_parsing(self, host = None):
		if not host: raise ValueError("No valid host was given")
		elif host == KICKASS: self._torrent_parsing_kat() # host is kickass so call a function to handle it
		else : raise ValueError("Unknown host given")

	''' Parse acording to Kickass structure '''
	def _torrent_parsing_kat(self):
		tm_pattern = re.compile('Download torrent file|Torrent magnet link') # torrent and magnets pattern
		# looking at the html all the information about the torrent can be found as follows
		# torrent_ids comes as a list of tuples being the first element the torrent name and the last its link
		# torren_files and magnets is a list of torrent links and magnets respectivly
		# torrent_info comes as: size, files, age, seeds, peers. Repeated for each torrent
		torrent_ids = [(r.get_text(), r.get('href')) for r in self.btree.find_all('a', attrs = {'class', 'cellMainLink'})]
		tm_links = [r.get('href') for r in self.btree.find_all('a', {'title' : tm_pattern})]
		torrent_info = [r.get_text() for r in self.btree.find_all('td', {'class', 'center'})]

		# get everything nice and sorted as list of Torrent structures
		# compensate the fact that links and info are sequentialy on the list
		for i, n in enumerate(torrent_ids):
			to_add = Torrent(name = n[0],
					link = n[1],
					magnet = tm_links[2*i + 0],
					tor_file = tm_links[2*i + 1],
					size = torrent_info[5*i + 0],
					files = torrent_info[5*i + 1],
					age = torrent_info[5*i + 2],
					seeds= torrent_info[5*i + 3],
					peers = torrent_info[5*i + 4])
			self.parsed.append(to_add)
		return self.parsed

	''' Reset class attributes '''
	def reset(self):
		self.parsed = []
		self.btree = None

	def close(self):
		pass


