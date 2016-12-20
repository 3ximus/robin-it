import re

import requests
from bs4 import BeautifulSoup

from libs.torrent import Torrent

class PirateBay:
	'''Namespace with search function for PirateBay'''
	@staticmethod
	def search(query, base_url):
		'''Search pirate bay and return list of Torrent instances'''

		search_url = base_url + "/search/" + query + "/0/7/0"
		response = requests.get(search_url).text
		soup = BeautifulSoup(response, 'lxml')
		torrents = []
		results_table = soup.find(id="searchResult")
		pattern = re.compile(r'Uploaded (.*), Size (.*), ULed by')

		if not results_table: # no results found
			return []
		# iterate over table rows
		for row in results_table.find_all('tr'):
			# get all table cells , cell #0 is useless, only represents the
			# category
			cells = row.find_all('td')
			if cells:  # skip the table legend on top (parses to empy list)
				a = cells[1].find_all('a')  # cell #1 contains name and magnet link
				match = pattern.match(cells[1].font.text)
				tor = Torrent(
					name=a[0].text,
					url=base_url + a[0]['href'],
					magnet=a[1]['href'],
					seeds=int(cells[2].text),  # column #2 contains seeds
					peers=int(cells[3].text),  # column #3 contains leechs
					age=match.group(1).encode('ascii', 'replace').decode('ascii'), # contains non ascii
					size=match.group(2).encode('ascii', 'replace').decode('ascii'), # contains non ascii
					host=base_url
				)
				torrents.append(tor)
		return torrents

