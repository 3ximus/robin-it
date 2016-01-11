#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

import sys

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from random import random, randint
from functools import partial

# yellow / green theme colors
theme_colors = [[0.98, 0.97, 0.08], # yellow
				[0.78, 0.9, 0.21], # yellowish green
				[0.11, 0.95, 0.55], # greenish blue
				[0.2, 0.8, 0.2, 0.5]] # green

# --- BACKGROUND BOKEH GLOBALS ---
B_SPAWNED = 2 # set number of bokehs spawned each time
B_SPAWN_TIME_INTERVAL = 1 # time interval between each spawn
B_MAX_OPACITY = 0.3 # maximum opacity a bokeh can reach
B_OPACITY_RATE = 0.04 # rate of opacity change, less == more screen time
B_MIN_SIZE = 20 # minimum bookeh size
B_MAX_SIZE = 150 # maximum bokeh size

# ------------------------------
#         BACKGROUND
# ------------------------------

class BokehLight(Widget):
	_timer_c = 0

	# Set default values
	velocity = ListProperty([0.1, 0.1]) # bokeh velocity
	r_color = ListProperty([1, 1, 1]) # bokeh color
	r_width = NumericProperty(100) # bokeh width
	r_height = NumericProperty(100) # bokeh size
	max_opacity = NumericProperty(1) # maximum opacity a particle can reach
	_opacity = NumericProperty(0.01) # starting opacity
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
			self.slope_invert = True # make invert only happen once
		# calculate new opacity
		self._opacity += self._timer_c * self.slope * 0.001

''' Background containing moving bokeh lights spawned and moving randomly '''
class Background(FloatLayout):
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
		new_bokeh.center_y = -10 # little bellow the screen
		new_bokeh.center_x = self.center_x + randint(-10,10) * self.center_x/10
		# since they spawn on the bottom, make them go up and to the sides
		new_bokeh.velocity[0] = randint(-10, 10) * 0.02
		new_bokeh.velocity[1] = 0.1 + random() * 0.2
		new_bokeh.r_color = theme_colors[randint(0, len(theme_colors) -1 )]
		new_bokeh.max_opacity = B_MAX_OPACITY - random() * 0.2 # max value opacity cna reach
		size_val = randint(B_MIN_SIZE, B_MAX_SIZE)
		# set size
		new_bokeh.r_width = size_val
		new_bokeh.r_height = size_val
		self.add_widget(new_bokeh) # actually spawn the bockeh


class ImagePoster(ButtonBehavior, AsyncImage):
	pass

class ImageBanner(ButtonBehavior, AsyncImage):

	''' Set on_press action'''
	def on_press(self):
		pass

class ShowsGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ShowsGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_height=self.setter('height'))
		for i in range(30):
			img = ImageBanner(
				source='http://thetvdb.com/banners/graphical/262407-g11.jpg')
			self.add_widget(img)

	''' Sets amount of columns when layout streches '''
	def on_size(self, *largs):
		if self.right < 650: self.cols = 1
		elif self.right < 980: self.cols = 2
		else: self.cols = 3

''' Contains show information '''
class ItemScroller(ScrollView):
	def __init__(self, **kwargs):
		super(ItemScroller, self).__init__(**kwargs)

# ------------------------------
#            SCREENS
# ------------------------------

class ShowsMainScreen(Screen):
	pass

class AllShowsScreen(Screen):
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

# ------------------------------------
#     SCREEN BEHAVIOR / SETTIGNS
# ------------------------------------

# EMPTY

# ------------------------------------
#           SCREEN MANAGER
# ------------------------------------
screen_manager = ScreenManager(transition=SlideTransition())
screen_manager.add_widget(MainScreen(name = 'main_screen'))
screen_manager.add_widget(ShowsMainScreen(name = 'shows_main_screen'))
screen_manager.add_widget(AllShowsScreen(name = 'all_shows_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

# ------------------------------------
#          THE ROOT WIDGET
# ------------------------------------
root = FloatLayout()
root.add_widget(Background())
root.add_widget(screen_manager)
root.add_widget(InfoContainer())

''' APP CLASS '''
class RobinItApp(App):
	def build(self):
		return root

if __name__ == '__main__':
	RobinItApp().run()

