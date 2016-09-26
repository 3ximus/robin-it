'''
Library containing parser to scrap web pages
Latest Update - v1.1
Created - 28.12.15
Copyright (C) 2015 - eximus
'''
import re
from bs4 import BeautifulSoup
from torrent import Torrent

KICKASS = "http://kickasstorrents.to/"

class Torrent_BS4():
	'''Beautiful Soup 4 Custom parser

	Parser class derivation of BeautifulSoup4
	Returns a tuple with Torrent class instances
	'''
	def __init__(self):
		self.parsed = []
		self.btree = None # not an actual btree but a 'beautiful tree'

	def feed(self, html, parse_for='torrent', host = KICKASS):
		'''Callable feed method

		Receives the content to parse, or the open filedescriptor and how to parse it
		'''
		self.btree = BeautifulSoup(html, "lxml") # parse the webpage with lxml parser
		if parse_for == 'torrent': self._torrent_parsing(host = host) # TODO pass another host if needed
		else: raise ValueError("Unknown parser option given")

	def _torrent_parsing(self, host = None):
		''' Prepare for parsing according to host structure '''
		if not host: raise ValueError("No valid host was given")
		elif host == KICKASS: self._torrent_parsing_kat() # host is kickass so call a function to handle it
		else : raise ValueError("Unknown host given")

	def _torrent_parsing_kat(self):
		''' Parse acording to Kickass structure '''
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
					#magnet = tm_links[2*i + 0], # not working on KAT
					tor_file = tm_links[i],
					size = torrent_info[5*i + 0],
					files = torrent_info[5*i + 1],
					age = torrent_info[5*i + 2],
					seeds= torrent_info[5*i + 3],
					peers = torrent_info[5*i + 4],
					host = KICKASS)
			self.parsed.append(to_add)
		return self.parsed

	def _torrent_parsing_pirate_tv(self):
		''' Parse acording to pirate tv structure '''
		pass

	def reset(self):
		''' Reset class attributes '''
		self.parsed = []
		self.btree = None

	def close(self):
		pass


