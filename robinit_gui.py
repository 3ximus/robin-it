#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

import sys

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Line
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from random import random, randint
from functools import partial

# yellow / green theme colors
theme_colors = [[0.98, 0.97, 0.08], [0.78, 0.9, 0.21],[0.11, 0.95, 0.55],[0.2, 0.8, 0.2, 0.5]]

# --- BOKEH ---
B_SPAWNED = 2 # set number of bokehs spawned each time
B_SPAWN_TIME_INTERVAL = 1 # time interval between each spawn
B_MAX_OPACITY = 0.2 # maximum opacity a bokeh can reach
B_OPACITY_RATE = 0.2 # this is tied to the amount of time it is on the screen
B_MIN_SIZE = 20 # minimum bookeh size
B_MAX_SIZE = 150 # maximum bokeh size

class BokehLight(Widget):
	_timer_c = 0
	# Set default values
	velocity = ListProperty([0.1, 0.1])
	r_color = ListProperty([1, 1, 1])
	r_width = NumericProperty(100)
	r_height = NumericProperty(100)
	max_opacity = NumericProperty(1)
	_opacity = NumericProperty(0.001) # starting opacity
	slope = B_OPACITY_RATE # rate that opacity changes
	slope_invert = False # limit the inversion of the slope to happen only once

	def __init__(self, **kwargs):
		super(BokehLight, self).__init__(**kwargs)
		Clock.schedule_interval(self.update, 1/60) # 60 times per sec

	def update(self, dt):
		self._timer_c += dt
		# update position
		self.x += self.velocity[0]
		self.y += self.velocity[1]
		# opacity control
		if self._opacity >= self.max_opacity and not self.slope_invert:
			self.slope = 0 - self.slope # invert slope
			self.slope_invert = True
		# calculate new opacity
		self._opacity += self._timer_c * self.slope * 0.001

''' Background containing moving bokeh lights spawned and moving randomly '''
class Background(FloatLayout):
	bokeh_list = ListProperty([])

	def __init__(self, **kwargs):
		super(Background, self).__init__(**kwargs)
# spawn bokeh lights in defined intervals
# use a callback function with partial to set amount of spawned bokeh per clock time
		Clock.schedule_interval(partial(self.chain_spawn, B_SPAWNED), B_SPAWN_TIME_INTERVAL)
		Clock.schedule_interval(self.remove_hidden, 0.3) # 3.33 times per sec

	def remove_hidden(self, dt):
		# remove decayed bokehs
		for bok in self.children:
			if bok._opacity <= 0:
				self.remove_widget(bok)

	'''Spawn multiple'''
	def chain_spawn(self, n, *largs):
		for i in range(n):
			self.spawn()

	''' Spawns a bokeh light '''
	def spawn(self):
		new_bokeh = BokehLight()
		# spawning position
		new_bokeh.center_y = -10
		new_bokeh.center_x = self.center_x + randint(-10,10) * self.center_x/10
		# since now they spawn on left side, make them move up and right
		new_bokeh.velocity[0] = randint(-10, 10) * 0.02
		new_bokeh.velocity[1] = 0.1 + random() * 0.2
		new_bokeh.r_color = theme_colors[randint(0, len(theme_colors) -1 )]
		new_bokeh.max_opacity = B_MAX_OPACITY - random() * 0.2 # max value opacity cna reach
		size_val = randint(B_MIN_SIZE, B_MAX_SIZE)
		# set size
		new_bokeh.r_width = size_val
		new_bokeh.r_height = size_val
		self.add_widget(new_bokeh) # actually spawn the bockeh

class ShowsMainScreen(Screen):
	pass

class MoviesMainScreen(Screen):
	pass

class MainScreen(Screen):
	pass

''' Version and author information '''
class InfoContainer(FloatLayout):
	pass

# ---------------------------------------------
#             LOAD .kv FILE
Builder.load_file('gui_style/robinit.kv')
# ---------------------------------------------

# create the screen manager
screen_manager = ScreenManager(transition=WipeTransition())
screen_manager.add_widget(MainScreen(name = 'main_screen'))
screen_manager.add_widget(ShowsMainScreen(name = 'shows_main_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

# make the root layout containing the screen manager and the global background
root = FloatLayout()
root.add_widget(Background())
root.add_widget(screen_manager)
root.add_widget(InfoContainer())

class RobinItApp(App):
	#kv_directory = 'gui_style'
	def build(self):
# set root widget to be the screen manager
		return root

if __name__ == '__main__':
	RobinItApp().run()

