from sys import platform as _platform
if _platform =="linux" or _platform == "linux2":
	from cx_Freeze import setup, Executable

	#Run with python2 setup.py build

	# Dependencies are automatically detected, but it might need
	# fine tuning.
	buildOptions = dict(packages = [], excludes = [])

	base = 'Console'

	executables = [
	    Executable('robinit_console.py', base=base, targetName = 'robinit_console_v1_0_1')
	]

	setup(name='robinit',
	      version = '0.2',
	      description = 'TV Show Tracker and downloader -- console version',
	      options = dict(build_exe = buildOptions),
	      executables = executables)
elif _platform == "win32":
	from distutils.core import setup
	import py2exe

	setup(console=['robinit_console.py'])

elif _platformt == "darwin":
	pass
