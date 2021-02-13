from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle
from kivy.properties import (NumericProperty, BoundedNumericProperty, ObjectProperty)


class GameMenu(FloatLayout):
    difficulty = BoundedNumericProperty(3, min=1, max=5)
    newButton = ObjectProperty(None)
    quitButton = ObjectProperty(None)
    difSlider = ObjectProperty(None)
    difLabel = ObjectProperty(None)
    newFlag = ObjectProperty(None)
    quitFlag = ObjectProperty(None)
# ------------------------------------------------------
    def new_game(self,instance):
        self.newFlag = True
        self.quitFlag = False
        print('gameMenu.new_game','new=',self.newFlag,'quit=',self.quitFlag)
# ------------------------------------------------------
    def quit(self,instance):       
        self.newFlag = False
        self.quitFlag = True
        print('gameMenu.quit','new=',self.newFlag,'quit=',self.quitFlag)
# ------------------------------------------------------
    def __init__(self, difficulty=3, *args): 
        super().__init__(*args)
        self.build(difficulty=difficulty)
# ------------------------------------------------------
    def add_buttons(self):
        self.newButton = Button(text='NEW MAZE',size_hint=(.5,.5),pos_hint={'x': 0,'top': 1},background_normal='assets/green_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.newButton.bind(texture_size=callback)
        self.newButton.bind(on_press=self.new_game)
        self.quitButton = Button(text='quit',size_hint=(.5,.5),pos_hint={'x': .5,'top': 1},background_normal='assets/red_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.quitButton.bind(texture_size=callback)
        self.quitButton.bind(on_press=self.quit)
# ------------------------------------------------------
    def add_level_selector(self):
        self.difLabel = Label(text=self.getDifficultyText(self.difficulty),size_hint=(1,.5),pos_hint={'center_x': .5,'top': .75},font_size=self.newButton.font_size)
        self.difSlider = Slider(min=1, max=5,orientation='horizontal',size_hint=(1,.5),pos_hint={'center_x': .5, 'y': 0},value_track=False)
        self.difSlider.value = self.difficulty
        def callback(instance, value):
            self.difficulty = round(self.difSlider.value)
            self.difLabel.text = self.getDifficultyText(value=self.difficulty)
        self.difSlider.bind(value=callback)
# ------------------------------------------------------
    def build(self,difficulty):
        self.size_hint = (.75,.75) 
        self.pos_hint = {'x': .25, 'top': .75}
        self.anchor_x = 'center'
        self.anchor_y = 'top'
        self.newFlag = False
        self.quitFlag = False
        self.difficulty = difficulty
#
        self.add_buttons()
        self.add_level_selector()
#
        self.add_widget(self.newButton)
        self.add_widget(self.quitButton)
        self.add_widget(self.difSlider)
        self.add_widget(self.difLabel)
        self.canvas.ask_update()
# ------------------------------------------------------
    def update(self):
        self.canvas.ask_update()
# ------------------------------------------------------
    def getDifficultyText(self,value):
        switcher = {
            1: "Easy",
            2: "Moderate",
            3: "Standard",
            4: "Hard",
            5: "Maximum"
            }
        item = switcher.get(value,'')
        return item
