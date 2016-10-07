
'''
Configuration File Manager
Manages a given configuration file
Created - 7.10.16
Copyright (C) 2016 - eximus
'''

CONFIG_FILE = 'robinit.conf'
DEFAULTS = {}

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
		global CONFIG_FILE # use this in order to not have the file atribute
		CONFIG_FILE = config_file # this way we can just save self.__dict__
		global DEFAULTS
		if default_config and type(default_config) == dict:
			DEFAULTS = default_config
			self.update(default_config)

		self.load()
		if start_config and type(start_config) == dict:
			self.update(start_config)
			self.save()

	def has_property(self, prop):
		return prop in self.__dict__

	def __getitem__(self, key): # able to use config_instance['key']
		return self.__dict__[key]

	def __setitem__(self, key, value): # able to use config_instance['key'] = val
		self.__dict__[key] = value

	def __delitem__(self, key): # able to use del(config_instance['key'])
		del(self.__dict__[key])

	def add_property(self, prop, value):
		if type(prop) != str:
			raise AttributeError("[\033[0;31mERROR\033[0m] Tried to add property to class with name not string")
		if type(value) != str and type(value) != bool and type(value) != unicode:
			print "[\033[0;33mWARNING\033[0m] Property %s value is not a string nor bool" % prop
		if value != "":
			self.__dict__.update({prop:value})

	def update(self, content):
		for k in content: self.add_property(k, content[k])

	def load(self):
		'''Loads a config file to the self.__dict__ variable'''
		try:
			with open(CONFIG_FILE, 'r') as fp:
				for n, line in enumerate(fp):
					line.strip(' ')
					if line[0] == '#' or line[0] == '\n': continue
					line = [s.strip('\n') for s in line.split(' ')]
					if len(line) != 2 or line[1] == "":
						raise ValueError("[\033[0;31mERROR\033[0m] Line %d in %s: \" %s \"" % (n, CONFIG_FILE, ' '.join(line)))
					key, value = line
					if value == 'True': value = True
					elif value == 'False': value = False
					self.update({key : value})
		except IOError: return None # file doesnt exist
		return self.__dict__

	def save(self):
		with open(CONFIG_FILE, 'w') as fp:
			for key in self.__dict__:
				if key in DEFAULTS and self.__dict__[key] == DEFAULTS[key]:
					continue
				fp.write("%s %s\n" % (key, self.__dict__[key]))
