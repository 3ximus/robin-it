#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

__version__ = '1.3'

# ------- KIVY IMPORTS ----------
from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
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
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, ObjectProperty, OptionProperty
# ------- OTHER IMPORTS ----------
from random import random, randint
from functools import partial
import os, sys
# ------- USER API ----------
from robinit_api import UserContent
import webbrowser

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

# --- SELECTION BOX GLOBALS ---
SB_SIZE = 1 # height of selection box in percentage of selected item width

P_TEXT_SIZE = 25 # poster container text size
P_POSTER_HEIGHT = 280 # poster container height

B_BANNER_HEIGHT = 60 # banner container height

# --- SELECTION BAR GLOBALS ---
S_BAR_SIZE = 500
S_MOVEMENT_TIME = 0.2
S_BAR_OPACITY = 0.6

class Placeholder:
	'''  PLACEHOLDER CLASS '''
	pass

# ------------------------------
#         BACKGROUND
# ------------------------------

class Background(FloatLayout):
	'''Background configuration'''
	pass

# ------------------------------------
#               EVENTS
# ------------------------------------
class MultiEventDispatcher(EventDispatcher):
	def __init__(self, **kwargs):
		self.register_event_type('on_selection')
		self.register_event_type('on_state_update')
		super(MultiEventDispatcher, self).__init__(**kwargs)

	def select(self, what_is_selected, linked_content , value):
		'''Function to trigger on_selection event

		Arguments:
		what_was_selected -- instance of GUI selection
		linked_content -- instance of content that the GUI "points" to
		value -- True if seleced, False if unselected
		'''
		self.dispatch('on_selection', what_is_selected, linked_content, value)

	def update_gui(self, *args):
		'''Function to trigger on_state_update event'''
		self.dispatch('on_state_update', *args)

	def on_selection(self, what_is_selected, linked_content, value, *args):
		'''Default handler for the on_selection event'''
		pass

	def on_state_update(self, *args):
		'''Default handler for the on_state_update event'''
		pass

	# GENERATE EVENT DISPATCHERS

event_manager = MultiEventDispatcher()

# ------------------------------
#            SELECTOR
# ------------------------------

class Selector(FloatLayout):
	'''Handles item selection

	This is binded to on_selection event by default
	but can be binded to a specific method with bind_to(<method>)
	'''
	selected_list = ListProperty(0) # amount of selected items
	s_raised = BooleanProperty(False) # selection menu raised

	def __init__(self, **kwargs):
		super(Selector, self).__init__(**kwargs)
		if side_bar: # add side_bar
			self.show_side_bar = ShowSideBar()
			self.add_widget(self.show_side_bar)
		self.allow_side_bar=side_bar
		event_manager.bind(on_selection=self.handle_selection)

	def bind_to(self, method, unbind_selector=False):
		'''Binds the new function method passed to the on_selection event

		If unbind_selctor is passed it will unbind this selector and
		only bind the given funtion
		'''
		if unbind_selector: event_manager.unbind(on_selection=self.handle_selection)
		event_manager.bind(on_selection=method)

	def bind(self):
		'''Binds the selector default handler to on_selection event'''
		event_manager.bind(on_selection=self.handle_selection)

	def unbind(self):
		'''Unbinds the selector default handler from on_selection event'''
		event_manager.unbind(on_selection=self.handle_selection)
	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Adds selected item and its link to a list or removes them'''
		if value: self.selected_list.append((what_was_selected, linked_content))
		else: self.selected_list.remove((what_was_selected, linked_content))


	def on_selected_list(self, instance, value):
		'''Called when self.selected_list content is changed'''
		if self.allow_side_bar: # if side bar is allowed
			if len(value) == 0: self.s_raised = False
			elif not self.s_raised: self.s_raised = True

	def on_s_raised(self, instance, value):
		'''Called when self.s_raised value is changed'''
		if value == True: self.raise_selection_menu()
		else: self.lower_selection_menu()

	def raise_selection_menu(self):
		'''Raises the selection menu'''
		self.show_side_bar.raise_bar()

	def lower_selection_menu(self):
		'''Raises the selection menu'''
		self.show_side_bar.lower_bar()

	def clear_selected(self):
		'''Clear everything from the selected list'''
		for tup in self.selected_list:
			tup[0].selected = False # triggering unselect
		self.selected_list = []

class SingleSelector(Selector):
	'''Handles single item selection'''

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Overload function. Only allows 1 selected item'''
		if value:
			self.clear_selected()
			self.selected_list.append((what_was_selected, linked_content))
		else: self.clear_selected()

class SelectionMenuBar(Widget):
	pass

class ShowSideBar(SelectionMenuBar):
	def __init__(self, **kwargs):
		super(ShowSideBar, self).__init__(**kwargs)
		self.size_hint_x = None
		self.width = S_BAR_SIZE
		self.opacity = 0

	def on_size(self, *args):
		''' Called to correctly set initial position on resize '''
		self.x = self.right

	def raise_bar(self):
		''' Raise the side menu '''
		Animation.cancel_all(self)
		anim = Animation(x=root.right - S_BAR_SIZE, y=0, duration=S_MOVEMENT_TIME, transition = 'in_cubic')
		anim.bind(on_start = self.on_start)
		anim.start(self)

	def lower_bar(self):
		''' Lower the side menu '''
		Animation.cancel_all(self)
		anim = Animation(x=root.right, y=0, duration=S_MOVEMENT_TIME, transition = 'out_cubic')
		anim.bind(on_complete = self.on_complete)
		anim.start(self)

	def on_start(self, *args):
		''' Binded to the begining of the raise animation '''
		self.opacity = S_BAR_OPACITY # show bar

	def on_complete(self, *args):
		''' Binded to the completion of lower animation '''
		self.opacity = 0 # hide bar after completion

# ------------------------------------
#           ITEM CONTAINERS
# ------------------------------------

class ItemContainer(ButtonBehavior, FloatLayout):
	'''General item conatiner definition -- see overloads

	Triggers on_selected events
	Must contain a link to the Content it displays
	Its usable displayed atributes are generally
		image, title and description
	Other atributes may be added in specific instances
	Check derived classes for specific attributes and variations
	The status variable can take the values described, and should be used as follows
		unwatched -- available but not watched (mainly for tv shows)
		watched -- watched until this point (mainly for tv shows)
		completed -- completed (and watched for tv shows)
		pending -- not available yet (mainly for movies)
	'''
	selected = BooleanProperty(False)
	linked_content = ObjectProperty(None)
	status_box = None
	status = OptionProperty("pending", options=["watched",
												"unwatched",
												"completed",
												"pending"])

	def __init__(self, linked_content, **kwargs):
		super(ItemContainer, self).__init__(**kwargs)
		self.linked_content = linked_content
		self.selection_box = SelectionBox(size_hint=(None, None))

	def on_press(self):
		'''Image is pressed behavior'''
		if self.selected > 0:
			self.selected = False
			# launch on_selected event
			event_manager.select(self, self.linked_content, False)
		else:
			self.selected = True
			# launch on_selected event
			event_manager.select(self, self.linked_content, True)

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		pass

	def on_status(self, instance, value):
		'''Action to take when self.status changes'''
		if value == "watched": self._set_status_box(MarkWatchedBox)
		elif value == "unwatched": self._set_status_box(MarkUnwatchedBox)
		elif value == "completed": self._set_status_box(MarkCompletedBox)
		elif value == "pending": self._set_status_box(MarkPendingBox)
		else: raise ValueError("Wrong State on ItemContainer")

	def _set_status_box(self, box_type):
		'''Sets status box to a given box class and displays it

		Must not be called directly
		Allways change the value of status to automaticly trigger this function
		'''
		if self.status_box: self.remove_widget(self.status_box)
		self.status_box = box_type(size_hint=(None, None))
		self.add_widget(self.status_box)

	def on_size(self, *args):
		'''Action taken on resize, will call update structure'''
		self.update_structure()

	def update_structure(self):
		'''Called on resize, must contain size and position rules for selection and status boxes'''
		self.status_box.size = self.size
		self.status_box.pos = self.pos

	def on_selected(self, instance, value):
		'''Action to take when self.selected changes'''
		if value: self.select_effect()
		else: self.unselect_effect()

	def select_effect(self):
		'''Remove status box to "make space" for the select effect'''
		if self.status_box: self.remove_widget(self.status_box)
		self.add_widget(self.selection_box)

	def unselect_effect(self):
		'''Add status box again after deselection'''
		self.remove_widget(self.selection_box)
		self.add_widget(self.status_box)

class BannerContainer(ItemContainer):
	'''General container with only the banner -- see overloads'''
	def __init__(self, **kwargs):
		super(BannerContainer, self).__init__(**kwargs)
		self.image = ImageBanner(source=self.linked_content.banner)
		self.add_widget(self.image)

	def update_structure(self, *args):
		'''Update size and position of items'''
		super(BannerContainer, self).update_structure()
		# limit status box to image banner status box
		self.status_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.status_box.y = self.y
		self.status_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2
		# update image pos with own pos
		self.image.pos = self.pos
		# limit selection box to image banner
		self.selection_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.selection_box.y = self.y
		self.selection_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2

class ShowBannerContainer(BannerContainer):
	'''Show container with only the banner'''
	def __init__(self, **kwargs):
		super(ShowBannerContainer, self).__init__(**kwargs)
		self.update_status()

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		self.status = self.linked_content.get_status()

class PosterContainer(ItemContainer):
	'''General container with only the poster -- see overload'''
	def __init__(self, **kwargs):
		super(PosterContainer, self).__init__(**kwargs)
		self.image = ImagePoster(source=self.linked_content.poster)
		self.add_widget(self.image)

	def update_structure(self, *args):
		'''Update size and position of items'''
		super(PosterContainer, self).update_structure()
		# limit status box to image banner status box
		self.status_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.status_box.y = self.y
		self.status_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2
		# update image pos with own pos
		self.image.pos = self.pos
		# limit selection box to image banner
		self.selection_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.selection_box.y = self.y
		self.selection_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2

class ShowPosterContainer(PosterContainer):
	'''Show Container with poster and description'''

	def __init__(self, **kwargs):
		super(ShowPosterContainer, self).__init__(**kwargs)
		self.update_status() # will also generate  new labels
		self.add_widget(self.title_highlight)
		self.add_widget(self.title)
		self.add_widget(self.unwatched_count)
		self.add_widget(self.rating)
		self.add_widget(self.imdb)

	def update_structure(self, *args):
		'''Update size and position of items'''
		self.status_box.size = self.size
		self.status_box.pos = self.pos

		x_offset = (self.width-self.height*self.image.image_ratio)/2

		self.image.y = self.y
		self.image.x = self.x - x_offset

		self.title_highlight.pos = (self.x + self.height*self.image.image_ratio, self.y + P_POSTER_HEIGHT*0.8)
		self.title_highlight.width = self.width-self.height*self.image.image_ratio
		self.title_highlight.height = P_POSTER_HEIGHT*0.2

		self.title.pos = (self.x + x_offset, self.y + P_POSTER_HEIGHT*0.4)
		self.unwatched_count.pos = (self.x + x_offset, self.y + P_POSTER_HEIGHT*0.2)
		self.rating.pos = (self.x + x_offset, self.y - P_POSTER_HEIGHT*0)
		self.imdb.pos = (self.x + x_offset, self.y - P_POSTER_HEIGHT*0.2)

		self.selection_box.size = self.size
		self.selection_box.pos = self.pos

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		self.status = self.linked_content.get_status()

		self.title = Label(text=self.linked_content.name,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.title_highlight = ThemeHighlight()
		total_unwatched = 0
		for ep_list in self.linked_content.get_unwatched_episodes().values():
			total_unwatched += len(ep_list)
		self.unwatched_count = Label(text='Episodes to watch: %d' % total_unwatched,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.rating = Label(text='Rating: [color=ffbf00]%s[/color]' % self.linked_content.rating,
							markup=True,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.imdb = Label(text='[ref=imdb][color=00bfff]IMDB[/color][/ref]',
							markup=True,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.imdb.bind(on_ref_press=self.open_imdb_link)

	def open_imdb_link(self, instance, value):
		'''Open IMDB link'''
		webbrowser.open(self.linked_content.imdb_id)

# ------------------------------------
#               BOXES
# ------------------------------------

class SelectionBox(Widget):
	'''Box to mark selected items'''
	pass

class MarkWatchedBox(Widget):
	'''Box to mark watched items'''
	pass

class MarkUnwatchedBox(Widget):
	'''Box to mark unwatched items'''
	pass

class MarkCompletedBox(Widget):
	'''Box to mark completed items'''
	pass

class MarkPendingBox(Widget):
	'''Box to mark pending items'''
	pass

class ThemeHighlight(Widget):
	'''Box to put behind titles'''
	pass

# ------------------------------------
#            IMAGES
# ------------------------------------

class WebImage(AsyncImage):
	'''Image loaded from a url'''
	def darken_color(self):
		'''Apply darker image tint'''
		self.color = [0.5, 0.5, 0.5, 1]

	def reset_color(self):
		'''Reset image color to original'''
		self.color = [1, 1, 1, 1]

class ImagePoster(WebImage):
	pass

class ImageBanner(WebImage):
	pass

class EpisodeImage(WebImage):
	pass

# ------------------------------------
#             SHOWS GRID
# ------------------------------------
class ItemScroller(ScrollView):
	'''Container for scrollable Layouts'''
	pass

class ScrollableGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ScrollableGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_height=self.setter('height'))
		event_manager.bind(on_state_update=self.handle_state_update)

	def handle_state_update(self, *args):
		'''Called when update GUI event is triggered'''
		pass

class AllShowsGrid(ScrollableGrid):
	def handle_state_update(self, *args):
		'''Update Grid Content with all shows'''
		self.clear_widgets()
		completed = []
		watched = []
		unwatched = []
		for show in User_State.shows:
			item = ShowPosterContainer(linked_content=User_State.shows[show])
			item.size_hint_y = None
			item.height = P_POSTER_HEIGHT
			locals()[User_State.shows[show].get_status()].append(item)
		for item in unwatched + watched + completed:
			self.add_widget(item)

	def on_size(self, *args):
		'''Sets amount of columns when layout size is changed (resize)'''
		if self.right < 670: self.cols = 1
		elif self.right < 1015: self.cols = 2
		elif self.right < 1365: self.cols = 3
		else: self.cols = 4

class ShowsToWatchGrid(ScrollableGrid):
	def handle_state_update(self, *args):
		'''Update Grid Content with all shows'''
		self.clear_widgets()
		for show in User_State.shows:
			item = ShowBannerContainer(linked_content=User_State.shows[show])
			item.size_hint_y = None
			item.height = B_BANNER_HEIGHT
			if User_State.shows[show].get_status() == 'unwatched':
				self.add_widget(item)

	def on_size(self, *args):
		'''Sets amount of columns when layout size is changed (resize)'''
		if self.right < 670: self.cols = 1
		elif self.right < 1015: self.cols = 2
		elif self.right < 1365: self.cols = 3
		else: self.cols = 4

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
		'''Build The Popup'''
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

	def load_user(self, *args):
		''' Load user based on username input '''
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

	def generate_new_user(self):
		''' Generate a new user '''
		pass

class PopupShade(FloatLayout):
	pass

# ------------------------------
#            SCREENS
# ------------------------------

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

class ShowsMainScreen(Screen):
	pass

class AllShowsScreen(Screen):
	'''Screen containing a view of all shows'''
	def on_pre_enter(self):
		''' Executed before entering '''
		# catch selection events and handle by opening new screen with show view
		# TODO Handle this with the selector
		event_manager.bind(on_selection=self.handle_selection)
		# if a view screen was open, remove it
		try: self.manager.remove_widget(self.manager.get_screen('view_show'))
		except ScreenManagerException: pass

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Triggered when a on_selection event ocurrs'''
		if value:
			what_was_selected.selected = False # unselect
			self.new_screen(linked_content)
		else: # not likely this will be triggered
			pass

	def on_pre_leave(self):
		''' Executed before leaving '''
		event_manager.unbind(on_selection=self.handle_selection)

	def new_screen(self, show):
		'''Create new view show screen with'''
		screen = ShowViewScreen(name='view_show')
		screen.add_widget(ThemeTitle(text=show.name, pos=(self.center_x, self.top - 90)))
		# TODO SETUP THE NEW SCREEN WITH SHOW INFO
		self.manager.add_widget(screen)
		self.manager.transition.direction = 'up'
		self.manager.current = 'view_show'

class ShowViewScreen(Screen):
	pass

class ToWatchScreen(Screen):
	'''Screen with shows to watch'''
	def __init__(self, **kwargs):
		super(ToWatchScreen, self).__init__(**kwargs)

	def on_pre_enter(self):
		pass

	def on_size(self, *args):
		pass

	def on_pre_leave(self):
		pass

class MoviesMainScreen(Screen):
	pass

class InfoContainer(FloatLayout):
	'''Version and author information'''
	pass

class LoadingMessageContainer(FloatLayout):
	'''Loading Status information'''
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
screen_manager.add_widget(ToWatchScreen(name = 'to_watch_screen'))
screen_manager.add_widget(AllShowsScreen(name = 'all_shows_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

# ------------------------------------
#          THE ROOT WIDGET
# ------------------------------------
root = FloatLayout()
root.add_widget(Background())
root.add_widget(screen_manager)
root.add_widget(InfoContainer())
root.add_widget(LoadingMessageContainer())

class RobinItApp(App):
	''' APP CLASS '''
	def build(self):
		return root

if __name__ == '__main__':
	RobinItApp().run()

