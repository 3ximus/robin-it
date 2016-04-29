from cx_Freeze import setup, Executable

#Run with python2 setup.py build

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

base = 'Console'

executables = [
    Executable('robinit_console.py', base=base, targetName = 'robinit_console_v1.0.0')
]

setup(name='robinit',
      version = '1.0.0',
      description = 'TV Show Tracker and downloader -- console version',
      options = dict(build_exe = buildOptions),
      executables = executables)
