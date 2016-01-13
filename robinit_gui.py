#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

__version__ = '1.3'

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, ScreenManagerException
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.event import EventDispatcher
from kivy.animation import Animation
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, ObjectProperty
from random import random, randint
from functools import partial
import os, sys
from robinit_api import UserContent

# yellow / green theme colors
theme_colors = [[0.2, 0.8, 0.2, 0.5], # green
				[0.98, 0.97, 0.08], # yellow
				[0.78, 0.9, 0.21], # yellowish green
				[0.11, 0.95, 0.55]] # greenish blue

# default font
theme_font = 'gui_style/fonts/VertigoFLF.ttf'

# --- USER STATE ----
User_State = None
USER_STATE_DIR = "user/"
USER_STATE_FILE = ''

# --- BACKGROUND BOKEH GLOBALS ---
B_SPAWNED = 2 # set number of bokehs spawned each time
B_SPAWN_TIME_INTERVAL = 1 # time interval between each spawn
B_MAX_OPACITY = 0.3 # maximum opacity a bokeh can reach
B_OPACITY_RATE = 0.04 # rate of opacity change, less == more screen time
B_MIN_SIZE = 20 # minimum bookeh size
B_MAX_SIZE = 150 # maximum bokeh size

# --- SELECTION BAR GLOBALS ---
S_BAR_SIZE = 500
S_MOVEMENT_TIME = 0.2
S_BAR_OPACITY = 0.6

'''  PLACEHOLDER CLASS '''
class Placeholder:
	pass

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


# ------------------------------------
#               EVENTS
# ------------------------------------
class MultiEventDispatcher(EventDispatcher):
	def __init__(self, **kwargs):
		self.register_event_type('on_selection')
		self.register_event_type('on_state_update')
		super(MultiEventDispatcher, self).__init__(**kwargs)

	'''
	Function called on the event dispatcher to trigger a on_selection event
	Params  should be a s follows:
		what_was_selected: instance of GUI selection
		linked_content: instance of content that the GUI "points" to
		value: True if seleced, False if unselected
	'''
	def select(self, what_is_selected, linked_content , value):
		self.dispatch('on_selection', what_is_selected, linked_content, value)

	def update_gui(self, *args):
		self.dispatch('on_state_update', *args)

	''' Default handler for the on_selection event '''
	def on_selection(self, what_is_selected, linked_content, value, *args):
		pass

	''' Default handler for the on_state_update event '''
	def on_state_update(self, *args):
		pass

	# GENERATE EVENT DISPATCHERS

event_manager = MultiEventDispatcher()

# ------------------------------------
#             SHOWS GRID
# ------------------------------------

class ImageButton(ButtonBehavior, AsyncImage):
	selected = BooleanProperty(False)
	linked_content = Placeholder()

	''' When Image is pressed '''
	def on_press(self):
		if self.selected > 0:
			self.selected = False
			# launch selected event
			event_manager.select(self, self.linked_content, False)
		else:
			self.selected = True
			# launch selected event
			event_manager.select(self, self.linked_content, True)
	'''
	Catch self.selected change event
	Params:
		instance: represents self
		value: selection value, True if selected, False if unselected
	'''
	def on_selected(self, instance, value):
# TODO instead of colouring use rectangle in the canves BUT DONT FUCKING FORGET TO PUT
# pos: self.pos , OTHERWISE IT **FUCKING** WONT MOVE!!!
		if value: self.select_effect()
		else: self.unselect_effect()

	''' Apply effect of selected '''
	def select_effect(self):
		self.color = [0.5, 0.5, 0.5, 1]

	''' Apply effect of selected '''
	def unselect_effect(self):
		self.color = [1, 1, 1, 1]

class ImagePoster(ImageButton):
	pass

class ImageBanner(ImageButton):
	pass

class EpisodeImage(ImageButton):
	pass

class ShowsVerticalGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ShowsVerticalGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_height=self.setter('height'))
		event_manager.bind(on_state_update=self.handle_state_update)
		# generate grid content

	'''
	Called when update GUI event is triggered
	Default scenario displaying all shows
	'''
	def handle_state_update(self, *args):
		self.clear_widgets()
		# generate grid content
		for show in User_State.shows:
			source = User_State.shows[show].banner
			img = ImageBanner(source= source)
			img.linked_content = User_State.shows[show]
			self.add_widget(img)

	''' Sets amount of columns when layout size is changed (resize) '''
	def on_size(self, *largs):
		if self.right < 650: self.cols = 1
		elif self.right < 980: self.cols = 2
		else: self.cols = 3

class WatchedShowsVerticalGrid(ShowsVerticalGrid):
	'''
	Called when update GUI event is triggered
	Displays only watched shows
	'''
	def handle_state_update(self, *args):
		self.clear_widgets()
		# generate grid content
		for show in [show for show in User_State.shows if User_State.shows[show].watched]:
			source = User_State.shows[show].banner
			img = ImageBanner(source= source)
			img.linked_content = User_State.shows[show]
			self.add_widget(img)

class FollowingShowsVerticalGrid(ShowsVerticalGrid):
	'''
	Called when update GUI event is triggered
	Displays only following shows
	'''
	def handle_state_update(self, *args):
		self.clear_widgets()
		# generate grid content
		for show in [show for show in User_State.shows if not User_State.shows[show].watched]:
			source = User_State.shows[show].banner
			img = ImageBanner(source= source)
			img.linked_content = User_State.shows[show]
			self.add_widget(img)

class ShowsHorizontalGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ShowsHorizontalGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_width=self.setter('width'))
		event_manager.bind(on_state_update=self.handle_state_update)

	def handle_state_update(self, *args):
		self.clear_widgets()
		# generate grid content
		for show in User_State.unwatched_episodes():
			source = User_State.shows[show].poster
			img = ImagePoster(source= source)
			img.linked_content = User_State.shows[show]
			self.add_widget(img)

class EpisodesHorizontalGrid(GridLayout):
	def __init__(self, **kwargs):
		super(EpisodesHorizontalGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_width=self.setter('width'))

	''' create this grid '''
	def create(self, show):
		self.clear_widgets()
		for season in show.seasons:
			if not season.watched:
				for episode in season.episodes:
					source = episode.image
					img = EpisodeImage(source= source)
					img.linked_content = episode
			# FIXME BUG HERE
					self.add_widget(img)

	def handle_state_update(self, *args):
		print "Trying to update..."

	''' Sets amount of columns when layout size is changed (resize) '''
	def on_size(self, *largs):
		print self.top
		if self.top < 200: self.cols = 3
		elif self.top < 400: self.cols = 4
		else: self.cols = 5


''' Contains show information '''
class ItemScroller(ScrollView):
	pass

# ------------------------------
#            SELECTOR
# ------------------------------

class SelectionMenuBar(Widget):
	pass

class ShowSideBar(SelectionMenuBar):
	def __init__(self, **kwargs):
		super(ShowSideBar, self).__init__(**kwargs)
		self.size_hint_x = None
		self.width = S_BAR_SIZE
		self.opacity = 0
		#butt1 = RemoveShow()
		#butt2 = ToogleWatched()
		#self.add_widget(butt1)
		#self.add_widget(butt2)

	''' Called to correctly set initial position on resize '''
	def on_size(self, *args):
		self.x = self.right

	''' Raise the side menu '''
	def raise_bar(self):
		Animation.cancel_all(self)
		anim = Animation(x=root.right - S_BAR_SIZE, y=0, duration=S_MOVEMENT_TIME, transition = 'in_cubic')
		anim.bind(on_start = self.on_start)
		anim.start(self)

	''' Lower the side menu '''
	def lower_bar(self):
		Animation.cancel_all(self)
		anim = Animation(x=root.right, y=0, duration=S_MOVEMENT_TIME, transition = 'out_cubic')
		anim.bind(on_complete = self.on_complete)
		anim.start(self)

	''' Binded to the begining of the raise animation '''
	def on_start(self, *args):
		self.opacity = S_BAR_OPACITY # show bar

	''' Binded to the completion of lower animation '''
	def on_complete(self, *args):
		self.opacity = 0 # hide bar after completion

class SelectionButtons(FloatLayout):
	pass

'''
Handles item selection
This is intenteded to only catch on_selection events
Note: A selector doesn't bind itself to the on_selection event,
	due to possible conflicts events must be binded and unbinded manually
	to the handle_selection method
'''
class Selector(FloatLayout):

	selected_list = ListProperty(0) # amount of selected items
	s_raised = BooleanProperty(False) # selection menu raised

	def __init__(self, side_bar=True, **kwargs):
		super(Selector, self).__init__(**kwargs)
		# add a hidden selection menu ( hardcoded 1920 to be after the screen edge
		if side_bar:
			self.show_side_bar = ShowSideBar()
			self.add_widget(self.show_side_bar)
		self.allow_side_bar=side_bar

	'''
	Triggered when a on_selection event ocurrs
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the GUI
		linked_content: instance of linked content to GUI element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value: self.selected_list.append((what_was_selected, linked_content))
		else: self.selected_list.remove((what_was_selected, linked_content))

	'''
	Called when self.selected_list content is changed
	Sets self.s_raised in so that a menu is raised / lowered
	Params:
		instance: represents self
		value: list with new content
	'''
	def on_selected_list(self, instance, value):
		if self.allow_side_bar: # if side bar is allowed
			if len(value) == 0: self.s_raised = False
			elif not self.s_raised: self.s_raised = True

	'''
	Called when self.s_raised value is changed
	Used to raise/lower selection menu
	Params:
		instance: represents self
		value: new value
	'''
	def on_s_raised(self, instance, value):
		if value == True: self.raise_selection_menu()
		else: self.lower_selection_menu()

	''' Raises the selection menu '''
	def raise_selection_menu(self):
		self.show_side_bar.raise_bar()

	''' Raises the selection menu '''
	def lower_selection_menu(self):
		self.show_side_bar.lower_bar()

	''' Clear everything selected selections '''
	def clear_selected(self):
		for tup in self.selected_list:
			tup[0].selected = False
		self.selected_list = []

class SingleSelector(Selector):
	'''
	Triggered when a on_selection event ocurrs
	This overloads the correspondent super function
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the GUI
		linked_content: instance of linked content to GUI element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value:
			self.clear_selected()
			self.selected_list.append((what_was_selected, linked_content))
		else: self.clear_selected()

# ------------------------------
#       BUTTONS & POPUPS
# ------------------------------

class ThemeTitle(Label):
	pass

class ThemeButton(Button):
	pass

class RemoveShow(ThemeButton):
	pass

class ToogleWatched(ThemeButton):
	pass

class UsernamePopup(Popup):
	def __init__(self, **kwargs):
		super(UsernamePopup, self).__init__(**kwargs)
		layout = BoxLayout(orientation='vertical')
		self.username = TextInput(text='fabio', font_name=theme_font, font_size=30, multiline=False)
		self.butt = ThemeButton(text='Validate', font_size=30)
		layout.add_widget(self.username)
		layout.add_widget(self.butt)
		self.content=layout
		# bind actions
		self.username.bind(on_text_validate=self.load_user) # when 'enter' is pressed
		self.butt.bind(on_release=self.load_user) # when button is clicked call load_user

	''' Load user based on username input '''
	def load_user(self, *args):
		user_name = self.username.text
		if  user_name != "":
			USER_STATE_FILE = "%srobinit_%s_%s%s" % (USER_STATE_DIR, __version__, user_name, '.pkl') # Only used to look for state file
			if not os.path.exists(USER_STATE_FILE): # no previous save file?
				# TODO GENERATE NEW USER POPUP
				pass
			else:
				global User_State # refer to the global User_State to make changes
				# set global User State
				User_State = UserContent(user_name)
				User_State.load_state(USER_STATE_DIR)
				event_manager.update_gui()
				self.parent.remove_popups()

	''' Generate a new user '''
	def generate_new_user(self):
		pass


class PopupShade(FloatLayout):
	pass

# ------------------------------
#            SCREENS
# ------------------------------

class AllShowsScreen(Screen):
	def __init__(self, **kwargs):
		super(AllShowsScreen, self).__init__(**kwargs)

	''' Executed before entering '''
	def on_pre_enter(self):
		# catch selection events and handle by opening new screen with show view
		event_manager.bind(on_selection=self.handle_selection)
		# remove a view screen when returning
		try: self.manager.remove_widget(self.manager.get_screen('view_show'))
		except ScreenManagerException: pass

	'''
	Triggered when a on_selection event ocurrs
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the GUI
		linked_content: instance of linked content to GUI element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value:
			what_was_selected.selected = False # unselect
			self.new_screen(linked_content)
		else: # not likely this will be triggered
			pass

	''' Executed before leaving '''
	def on_pre_leave(self):
		event_manager.unbind(on_selection=self.handle_selection)

	'''
	Create new view show screen with
	'''
	def new_screen(self, show):
		screen = ShowViewScreen(name='view_show')
		screen.add_widget(ThemeTitle(text=show.name, pos=(self.center_x, self.top - 90)))
		# TODO SETUP THE NEW SCREEN WITH SHOW INFO
		self.manager.add_widget(screen)
		self.manager.transition.direction = 'up'
		self.manager.current = 'view_show'

class ShowViewScreen(Screen):
	pass

class ShowsMainScreen(Screen):
	'''
	Builds the show main screen
	Structure is as follows:
	BoxLayout:
		Carousel:
			ItemScoller:
				ShowsHorizontalGrid:
					SingleSelector:
				EpisodesHorizontalGrid:
					Selector:
	'''
	def __init__(self, **kwargs):
		super(ShowsMainScreen, self).__init__(**kwargs)
		# create horizontal scroller with shows
		self.horizontal_scroller = ItemScroller()
		self.shows = ShowsHorizontalGrid(rows=1, spacing=5, size_hint_x=None)
		self.horizontal_scroller.add_widget(self.shows)
		# create the carousel
		self.carousel = Carousel()
		self.carousel.direction = 'bottom'
		self.carousel.add_widget(self.horizontal_scroller)
		# create the layout
		self.layout = BoxLayout(size_hint_y=None, pos=(0,100))
		self.layout.add_widget(self.carousel)
		# add layout
		self.add_widget(self.layout)

		self.show_selector = Selector()
		self.add_widget(self.show_selector)

	def on_pre_enter(self):
		# correctly resize the layout
		self.layout.height=root.top - 200
		# on_selection event on the event_manager will trigger a handle_selection
		event_manager.bind(on_selection=self.handle_selection)

	def on_size(self, *args):
		# correctly resize the layout
		self.layout.height=root.top - 200

	def on_pre_leave(self):
		self.show_selector.clear_selected()
		event_manager.unbind(on_selection=self.handle_selection)

	'''
	Triggered when a on_selection event ocurrs
	This will create a new carousel slide and switch to it
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the GUI
		linked_content: instance of linked content to GUI element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value:
			# unbind previous handler
			event_manager.unbind(on_selection=self.handle_selection)

			# create horizontal scroller with episodes
			self.episodes_scroller = ItemScroller()
			self.episodes = EpisodesHorizontalGrid(rows=3, spacing=5, size_hint_x=None)
			self.episodes_scroller.add_widget(self.episodes)
			self.episodes.create(linked_content)
			# set carousel
			self.carousel.add_widget(self.episodes_scroller)

			what_was_selected.selected = False # unselect
			self.carousel.load_slide(self.carousel.next_slide)

			# bind on selection events to the a selector
# TODO CHANGE SELECTOR BEHAVIOR TO BE A BOTTOM BAR
# ALSO ADD A BUTTON TO SELECTOR SO THAT IT CLEARS SELECTION
			event_manager.bind(on_selection=self.show_selector.handle_selection)

		else: # not likely this will be triggered
			pass

class MoviesMainScreen(Screen):
	pass

class MainScreen(Screen):
	def __init__(self, **kwargs):
		super(MainScreen, self).__init__(**kwargs)
		self.popup_shade = PopupShade()
		self.popup = UsernamePopup()
		self.add_widget(self.popup_shade)
		self.add_widget(self.popup)

	def on_size(self, *args):
		self.popup.center_x = self.right / 2
		self.popup.center_y = self.top / 2

	def remove_popups(self):
		self.popup.dismiss()
		self.remove_widget(self.popup)
		self.remove_widget(self.popup_shade)

''' Version and author information '''
class InfoContainer(FloatLayout):
	pass

# ---------------------------------------------
#             LOAD .kv FILE
Builder.load_file('gui_style/robinit.kv')
Builder.load_file('gui_style/items.kv')
# ---------------------------------------------

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

