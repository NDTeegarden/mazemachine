#kivy imports
from kivy.logger import Logger, LOG_LEVELS
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Rectangle, Color
from kivy.properties import (NumericProperty, BoundedNumericProperty, ObjectProperty, StringProperty, BooleanProperty, ListProperty)

#system imports
import sys

BUTTON_SIZE_HINT = (.3,.15)

class GameMenu(FloatLayout):
    difficulty = BoundedNumericProperty(3, min=1, max=5)
    soundOn = BooleanProperty(None)
    vibrateOn = BooleanProperty(None)
    newFlag = BooleanProperty(None)
    quitFlag = BooleanProperty(None)
    caption = StringProperty(None)
    captionLabel = ObjectProperty(None)      
# ------------------------------------------------------
    def __init__(self, difficulty=3, caption='test',soundOn=False,vibrateOn=False, *args): 
        super().__init__(*args)
        self.build(difficulty=difficulty,caption=caption,soundOn=soundOn,vibrateOn=vibrateOn)
# ------------------------------------------------------
    def add_buttons(self):
        self.newButton = Button(text='New Maze',size_hint=BUTTON_SIZE_HINT,pos_hint={'right': .87,'top': .75},background_normal='assets/green_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.newButton.bind(texture_size=callback)
        self.quitButton = Button(text='Quit',size_hint=BUTTON_SIZE_HINT,pos_hint={'right': .87,'top': .45},background_normal='assets/red_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.quitButton.bind(texture_size=callback)
#
        self.add_widget(self.newButton)
        self.add_widget(self.quitButton)
# ------------------------------------------------------
    def add_level_selector(self):
        self.difSelector = Selector(size_hint=(.35,1),pos_hint={'x': .05, 'top' : .85}) 
        self.add_widget(self.difSelector)
        self.difSelector.build(min=1, max=5,value=self.difficulty,orientation='vertical',title='Difficulty',descriptors=['Easy','Moderate','Challenging','Hard','Maximum'])
        self.difSelector.update_canvas()
        def callback(instance,value):
            self.difficulty = self.difSelector.value
        self.difSelector.bind(value=callback)
# ------------------------------------------------------
    def add_caption(self):
        l = Label(text=self.caption,size_hint=(1,.2),pos_hint={'center_x': .5,'top': 1}, font_size='36sp') 
        self.add_widget(l)
# ------------------------------------------------------
    def add_settings(self):
        self.settings = SettingsSection(soundOn=self.soundOn,vibrateOn=self.vibrateOn,size_hint=(.25,.15),pos_hint={'center_x': .4, 'center_y': .15})
        self.add_widget(self.settings)
        def callback(instance, value):
            self.soundOn = value
        self.settings.bind(soundOn=callback)
        def callback(instance, value):
            self.vibrateOn = value
        self.settings.bind(vibrateOn=callback)        
# ------------------------------------------------------
    def build(self,difficulty,caption,soundOn,vibrateOn):
        self.size_hint = (.75,.75) 
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.anchor_x = 'center'
        self.anchor_y = 'top'
        self.newFlag = False
        self.quitFlag = False
        self.difficulty = difficulty
        self.caption = caption
        self.soundOn = soundOn
        self.vibrateOn = vibrateOn
        self.init_canvas()
        self.add_caption()
        self.add_buttons()
        self.add_settings()
        self.add_level_selector()
        self.canvas.ask_update()
# ------------------------------------------------------
    def init_canvas(self,color=Color(0,0,0,.8),shape=None):
        self.color = color
        if shape == None:
            shape = self.default_shape()
        self.shape = shape
        self.canvas.clear()
        self.canvas.before.add(self.color)
        self.canvas.before.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)  
# ------------------------------------------------------
    def update(self):
        self.canvas.ask_update()
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def update_canvas(self,*args):
        try:
            self.update_shape()
        except Exception:
            Logger.warning('{}: failed to update_shape'.format(self))             

# #######################################################
class Selector(FloatLayout):
    slider = ObjectProperty(None)
    descriptors = ListProperty(None)
    descLabels = ListProperty(None)
    title = StringProperty(None)
    min = NumericProperty(None)
    max = NumericProperty(None)
    value = NumericProperty(None)
    color = ObjectProperty(None)

    def build(self,min,max,value,title,descriptors,orientation):
        self.shape = self.default_shape()
        self.color = Color(.2,.3,0,0)
        self.init_canvas()
        min = round(min)
        max = round(max)
        if value < min:
            value = min
        elif value > max:
            value = max
        else:
            value = round(value)
        self.min = min
        self.max = max
        self.value = value
        self.title = title
        self.descriptors = descriptors
        self.size = self.shape.size
        self.pos = self.shape.pos
        l = Label(text=title,size_hint=(1,.1),pos_hint={'center_x': .5, 'top': 1})
        self.add_widget(l)  
        sw=.4
        sh=.5
        self.slider = Slider(min=self.min,max=self.max,value=self.value,orientation=orientation,size_hint=(sw,sh),pos_hint={'center_x': .2, 'top': .9})
        self.add_widget(self.slider)
#
        self.descLabels = []        
        steps = self.max - self.min + 1
        y_increment = (sh) / steps   
        offset = self.min - 0
        x = .2
        for i in range(self.min,self.max+1):
            t=descriptors[i-offset]
            y = (1 - sh) + (i-offset-1) * y_increment
            l = Label(text=t,pos_hint={'x': x,'y': y},size_hint=(.6,y_increment))
            l.id = i
            l.disabled = (i != self.value)
            l.bind(on_touch_down=self._on_touch_down)
            self.descLabels.append(l)
            self.add_widget(l)
        def callback(instance, value):
            self.update()
        self.slider.bind(value=callback)
# ------------------------------------------------------
    def _on_touch_down(self, instance, touch):
        if instance.collide_point(touch.x,touch.y):  
            self.slider.value = instance.id 
        return False
# ------------------------------------------------------
    def init_canvas(self):
        self.canvas.clear()
        self.canvas.add(self.color)
        self.canvas.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)          
# ------------------------------------------------------
    def update(self):
        self.value = round(self.slider.value)
        offset = self.min - 0
        target = self.value
        for i in range(self.min,self.max+1):
            self.descLabels[i-offset].disabled = (i != target)
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def update_canvas(self,*args):
        try:
            self.update_shape()
        except Exception:
            Logger.warning('{}: failed to update_shape'.format(self))  
        self.update_widgets()                
# ------------------------------------------------------
    def update_widgets(self):
        for child in self.children:
            try:
                child.canvas.ask_update()
            except Exception:
                Logger.warning('{}: failed to update_shape'.format(self))  
# #######################################################
class PauseMenu(FloatLayout):
    soundOn = BooleanProperty(None)
    vibrateOn = BooleanProperty(None)
    resumeFlag = BooleanProperty(None)
    quitFlag = BooleanProperty(None)
    caption = StringProperty(None)
    captionLabel = ObjectProperty(None)      
# ------------------------------------------------------
    def __init__(self, caption='Paused', soundOn=False,vibrateOn=False, *args): 
        super().__init__(*args)
        self.build(caption=caption,soundOn=soundOn,vibrateOn=vibrateOn)
# ------------------------------------------------------
    def add_buttons(self):
        self.resButton = Button(text='Resume',size_hint=BUTTON_SIZE_HINT,pos_hint={'x': .5,'top': .8},background_normal='assets/green_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.resButton.bind(texture_size=callback)
        self.mainButton = Button(text='New Game',size_hint=BUTTON_SIZE_HINT,pos_hint={'x': .5,'top': .55},background_normal='assets/blue_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.mainButton.bind(texture_size=callback)        
        self.quitButton = Button(text='Quit',size_hint=BUTTON_SIZE_HINT,pos_hint={'x': .5,'top': .3},background_normal='assets/red_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.quitButton.bind(texture_size=callback)
#
        self.add_widget(self.resButton)
        self.add_widget(self.mainButton)        
        self.add_widget(self.quitButton)
# ------------------------------------------------------
    def add_caption(self):
        l = Label(text=self.caption,size_hint=(1,.2),pos_hint={'center_x': .5,'top': 1}, font_size='36sp') 
        self.add_widget(l)
# ------------------------------------------------------
    def add_settings(self):
        self.settings = SettingsSection(soundOn=self.soundOn,vibrateOn=self.vibrateOn,size_hint=(.25,.15),pos_hint={'center_x': .2, 'center_y': .5})
        self.add_widget(self.settings)
        def callback(instance, value):
            self.soundOn = value
        self.settings.bind(soundOn=callback)
        def callback(instance, value):
            self.vibrateOn = value
        self.settings.bind(vibrateOn=callback)  
# ------------------------------------------------------
    def build(self,caption,soundOn,vibrateOn):
        self.size_hint = (.75,.75) 
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.anchor_x = 'center'
        self.anchor_y = 'top'
        self.newFlag = False
        self.quitFlag = False
        self.caption = caption
        self.soundOn = soundOn
        self.vibrateOn = vibrateOn
        self.init_canvas()
        self.add_caption()
        self.add_buttons()
        self.add_settings()
        self.canvas.ask_update()
# ------------------------------------------------------
    def init_canvas(self,color=Color(0,0,0,.8),shape=None):
        self.color = color
        if shape == None:
            shape = self.default_shape()
        self.shape = shape
        self.canvas.clear()
        self.canvas.before.add(self.color)
        self.canvas.before.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)  
# ------------------------------------------------------
    def update(self):
        self.canvas.ask_update()
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def update_canvas(self,*args):
        try:
            self.update_shape()
        except Exception:
            Logger.warning('{}: failed to update_shape'.format(self))             

# #######################################################
class SettingsSection(GridLayout):
    soundOn = BooleanProperty(None)
    vibrateOn = BooleanProperty(None)
     
# ------------------------------------------------------
    def __init__(self, soundOn=False, vibrateOn=False, size_hint=(.25,.25),pos_hint={'center_x': .35, 'center_y': .15}, *args): 
        self.cols=2
        self.rows=2
        super().__init__(*args)
        self.build(soundOn=soundOn,vibrateOn=vibrateOn,size_hint=size_hint,pos_hint=pos_hint)
# ------------------------------------------------------
    def add_options(self, soundOn, vibrateOn):
        self.soundOn = soundOn
        self.vibrateOn = vibrateOn
        self.soundSwitch = Switch() 
        self.soundSwitch.active = soundOn        
        self.vibeSwitch = Switch() 
        self.vibeSwitch.active = vibrateOn
        def callback(instance, value):
            self.soundOn = value
            self.soundLabel.disabled = not value 
        self.soundSwitch.bind(active=callback)        
        def callback(instance, value):
            self.vibrateOn = value
            self.vibeLabel.disabled = not value
        self.vibeSwitch.bind(active=callback)
        self.soundLabel = Label(text='Sound')
        self.soundLabel.disabled=(not soundOn)
        self.vibeLabel = Label(text='Vibration')
        self.vibeLabel.disabled=(not vibrateOn) 
        self.add_widget(self.soundLabel)
        self.add_widget(self.vibeLabel)        
        self.add_widget(self.soundSwitch)
        self.add_widget(self.vibeSwitch)        
# ------------------------------------------------------
    def build(self,soundOn=False,vibrateOn=False,size_hint=(.25,.25),pos_hint={'center_x': .35, 'center_y': .15}):
        self.size_hint = size_hint 
        self.pos_hint = pos_hint
        self.init_canvas()
        self.add_options(soundOn, vibrateOn)
        self.canvas.ask_update()
# ------------------------------------------------------
    def init_canvas(self,color=Color(0,0,0,0),shape=None):
        self.color = color
        if shape == None:
            shape = self.default_shape()
        self.shape = shape
        self.canvas.clear()
        self.canvas.before.add(self.color)
        self.canvas.before.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)  
# ------------------------------------------------------
    def update(self):
        self.canvas.ask_update()
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def update_canvas(self,*args):
        try:
            self.update_shape()
        except Exception:
            Logger.warning('{}: failed to update_shape'.format(self))             

