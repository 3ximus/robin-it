'''
Library containing parser to scrap web pages
Latest Update - v1.1
Created - 28.12.15
Copyright (C) 2015 - eximus
'''


class Torrent():
    '''Torrent data structure'''

    def __init__(self, name='', url='', magnet='', tor_file='', seeds='', peers='', age='', files='', size='', host=''):
        '''Torrent data Constructor

        Parameters:
                name -- Contains the torrent Name
                url -- Contains the url to the torrent page
                magnet -- Manget url
                tor_file -- partial torrent file url (must be preceded with 'https:' and appended with '.torrent' to be a usable url
                seeds -- Torrent seeds
                peers -- Torrent peers
                age -- Simple representation of torrent age (hours, days, months, years)
                files -- Number of files a torrent contains
                host -- torrent host page
        '''
        self.name = name
        self.url = url
        self.magnet = magnet
        self.tor_file = tor_file
        self.size = size
        self.files = files
        self.age = age
        self.seeds = seeds
        self.peers = peers
        self.host = host

    def __repr__(self):
        rep = "Torrent:\n"
        rep += "[name] -- %s\n" % self.name
        if self.url:
            rep += "[url] -- %s\n" % self.url
        if self.magnet:
            rep += "[magnet] -- %s\n" % self.magnet
        if self.tor_file:
            rep += "[tor_file] -- %s\n" % self.tor_file
        if self.size:
            rep += "[size] -- %s\n" % self.size
        if self.files:
            rep += "[files] -- %s\n" % self.files
        if self.age:
            rep += "[age] -- %s\n" % self.age
        if self.seeds:
            rep += "[seeds] -- %s\n" % self.seeds
        if self.peers:
            rep += "[peers] -- %s\n" % self.peers
        rep += "[host] -- %s" % self.host
        return rep
