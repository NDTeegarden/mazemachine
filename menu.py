from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.properties import (NumericProperty, BoundedNumericProperty, ObjectProperty, StringProperty, BooleanProperty, ListProperty)


class GameMenu(FloatLayout):
    difficulty = BoundedNumericProperty(3, min=1, max=5)
    newButton = ObjectProperty(None)
    quitButton = ObjectProperty(None)
    difSelector = ObjectProperty(None)
    difLabel = ListProperty(None)
    newFlag = BooleanProperty(None)
    quitFlag = BooleanProperty(None)
    caption = StringProperty(None)
    captionLabel = ObjectProperty(None)
# ------------------------------------------------------
    def new_game(self,instance):
        self.newFlag = True
        self.quitFlag = False
        
# ------------------------------------------------------
    def quit(self,instance):  
        self.newFlag = False
        self.quitFlag = True
        sys.exit(0) 
        
# ------------------------------------------------------
    def __init__(self, difficulty=3, caption='test', *args): 
        super().__init__(*args)
        self.build(difficulty=difficulty,caption=caption)
# ------------------------------------------------------
    def add_buttons(self):
        print(self.top)
        self.newButton = Button(text='New Maze',size_hint=(.3,.2),pos_hint={'x': .5,'top': .8},background_normal='assets/green_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.newButton.bind(texture_size=callback)
        self.newButton.bind(on_press=self.new_game)
        self.quitButton = Button(text='Quit',size_hint=(.3,.2),pos_hint={'x': .5,'top': .4},background_normal='assets/red_roundedrect.png',background_down='assets/gray_roundedrect.png')
        def callback(instance,value):
            instance.text_size=instance.texture_size
        self.quitButton.bind(texture_size=callback)
        self.quitButton.bind(on_press=self.quit)
#
        self.add_widget(self.newButton)
        self.add_widget(self.quitButton)
# ------------------------------------------------------
    def add_level_selector(self):
        #print (self.newButton.pos)
        self.difSelector = Selector(size_hint=(.35,1),pos_hint={'x': 0, 'top' : .85}) 
        self.add_widget(self.difSelector)
        self.difSelector.build(min=1, max=5,value=self.difficulty,orientation='vertical',title='Difficulty',descriptors=['Easy','Moderate','Standard','Hard','Maximum'])
        #print(self.difSelector.shape.size)
        self.difSelector.update_canvas()
        def callback(instance,value):
            self.difficulty = self.difSelector.value
        self.difSelector.bind(value=callback)
# ------------------------------------------------------
    def add_caption(self):
        l = Label(text=self.caption,size_hint=(1,.2),pos_hint={'center_x': .5,'top': 1}) #,text_size=(self.width,None)
        self.add_widget(l)
# ------------------------------------------------------
    def build(self,difficulty,caption):
        self.size_hint = (.75,.75) 
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.anchor_x = 'center'
        self.anchor_y = 'top'
        self.newFlag = False
        self.quitFlag = False
        self.difficulty = difficulty
        self.caption = caption
        self.init_canvas()
        self.add_caption()
        self.add_buttons()
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
            print('widget',self,'failed to update_shape')             


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
        #print(self.shape.size,self.shape.pos)
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
        #print(y_increment)  
        offset = self.min - 0
        x = .2
        for i in range(self.min,self.max+1):
            t=descriptors[i-offset]
            #print(t)
            y = (1 - sh) + (i-offset-1) * y_increment
            #print(y)
            l = Label(text=t,pos_hint={'x': x,'y': y},size_hint=(.6,y_increment))
            l.disabled = (i != self.value)
            self.descLabels.append(l)
            self.add_widget(l)
        def callback(instance, value):
            self.update()
        self.slider.bind(value=callback)
# ------------------------------------------------------
    def init_canvas(self):
        #print('Cell.init_canvas')
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
        #print('size=',self.size,'pos=',self.pos)
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def update_canvas(self,*args):
        #print(self,'.update_canvas')
        try:
            self.update_shape()
        except Exception:
            print('widget',self,'failed to update_shape') 
        self.update_widgets()                
# ------------------------------------------------------
    def update_widgets(self):
        for child in self.children:
            try:
                child.canvas.ask_update()
            except Exception:
                print('widget',self,'failed to canvas.ask_update()') 
# -----------------------------------------------------


