
'''
Configuration File Manager
Manages a given configuration file
Created - 7.10.16
Copyright (C) 2016 - eximus
'''

import re
CAT_REGEX = re.compile(r"^\[.+\]$")
CONF_REGEX = re.compile(r"^\t.+=.+$")

class Config():
	'''Loads a config file if it exists otherwise creates a new one.
		If start config is a valid dictionary it uses it as the starting configuration,
			saving it to the new file
		If start config is given and file also exists the start config will update the
			configurations after the file is loaded
		If default_config is given, properties added with the same value as in the default_config
			will not be saved to the file, they will however be part of the class
	'''
	def __init__(self, config_file, start_config = None, default_config = None):
		self.dict = {}
		self.config_file = config_file

		# because having {} as default argument for default_config is considered
		# static and is # persistent across calls
		self.default_config = default_config if default_config and type(default_config) == dict else {}
		self.update(self.default_config)

		self.load()
		if start_config and type(start_config) == dict:
			self.update(start_config)
			self.save()

	def has_property(self, key, defaults=False):
		'''Check if key exists, if defaults is True it will search in the default configuration instead'''
		dic = self.dict if not defaults else self.default_config
		for category in dic.values():
			if key in category:
				return True
		return False

	def __getitem__(self, key): # able to use config_instance['key']
		for category in self.dict.values():
			if key in category:
				return category[key]
		raise KeyError("[ERROR] Config has no atribute \'%s\'" % key)

	def __setitem__(self, key, value): # able to use config_instance['key'] = val
		self.add_property(key, value)

	def __delitem__(self, key): # able to use del(config_instance['key'])
		for category in self.dict:
			if key in self.dict[category]:
				del(self.dict[category][key])

	def add_property(self, key, value, category=None):
		if type(key) != str:
			raise AttributeError("[ERROR] Tried to add property to class with name not string")
		if type(value) != str and type(value) != bool and type(value) != unicode and type(value) != int:
			print "[WARNING] Property %s value is not a string nor bool" % key
		cat = category if category else 'other'
		if cat not in self.dict:
			self.dict[cat] = {}
		self.dict[cat].update({key:value})

	def update(self, content):
		for k in content:
			if type(content[k]) == dict:
				for key in content[k]:
					self.add_property(key, content[k][key], category=k)
			else: self.add_property(k, content[k])

	def load(self):
		'''Loads a config file to the self.__dict__ variable'''
		try:
			with open(self.config_file, 'r') as fp:
				category = None
				for n, line in enumerate(fp):
					line = line.strip(' \n')
					if line[0] == '#' or line[0] == '\n': continue
					if CAT_REGEX.match(line):
						category = line.strip('[]')
						continue
					if CONF_REGEX.match(line):
						key, value = [x.strip() for x in line.strip('\t').split('=')]
						if value.lower() == 'true': value = True
						elif value.lower() == 'false': value = False
						try: value = int(value)
						except ValueError: pass
						self.add_property(key, value, category)
						print "[+] Loaded config Value: %s -> %s" % (key, value)
						continue
					raise SystemExit("[ERROR] Line %d in %s: \" %s \"" % (n+1, self.config_file, ''.join(line)))
		except IOError: return None # file doesnt exist
		return self.dict

	def save(self):
		with open(self.config_file, 'w') as fp:
			for category, content in self.dict.iteritems():
				writter = "[%s]\n" % category
				write = False # to help decide when to write (dont write if category is empty)
				for key, value in content.iteritems():
					if value == "" or (self.has_property(key, defaults=True) and value == self.default_config[category][key]):
						continue
					writter += "\t%s = %s\n" % (key, value)
					write = True
				if write: fp.write(writter)
