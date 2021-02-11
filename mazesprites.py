from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector


def GetKvColor(colordata=(0,0,0,0,'rgba')):
    r = colordata[0]
    g = colordata[1]
    b = colordata[2]
    a = colordata[3]
    mode = colordata[4]
    item = Color(r,g,b,a,mode=mode)
    return item

class SimpleSprite(Widget):
    color = ObjectProperty(None)
    shape = ObjectProperty(None)
    speed = ObjectProperty(None)
    
    def set_variables(self,size,pos,colordata,speed,shape,size_hint,obstacle):
        #print('Cell.set_variables')
        self.obstacle = obstacle
        self.speed = speed
        self.color = GetKvColor(colordata)
        self.size_hint = size_hint
        if shape != None:
            try:
                #print('shape=',shape)
                self.pos = shape.pos
                self.size = shape.size
                self.shape = shape
            except Exception:
                pass
        else:
            self.size = size
            self.pos = pos
            self.shape = self.default_shape()
            #print('shape=',shape,' , the default')


    def __init__(self,size=(16,16),pos=(0,0),colordata=(0,0,0,0,'rgba'),speed = 1,shape=None,size_hint = (1,1),obstacle=False):
        #print('Cell.__init__')
        super().__init__()
        self.set_variables(size=size,pos=pos,colordata=colordata,speed=speed,shape=shape,size_hint=size_hint,obstacle=obstacle)
        self.init_canvas()
        self.post_init()

    def post_init(self):
        #print('Cell.post_init')
        pass        

    def init_canvas(self):
        #print('Cell.init_canvas')
        self.canvas.clear()
        self.canvas.add(self.color)
        self.canvas.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)        

    def update_canvas(self,*args):
        #print(self,'.update_canvas')
        try:
            self.update_shape()
        except Exception:
            print('sprite',self,'failed to update_shape')       

    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s

    def move(self,vector):
        ##print('moving with vector',vector)
        if (vector != (0,0)):
            s = self.speed
            dx = vector[0] * s
            dy = vector[1] * s
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            self.pos = (x,y)

    def moveTo(self,pos):
        self.pos = (pos)                             
        

class Sprite(SimpleSprite):
    transparentcolor = ObjectProperty(None) 
    speed = ObjectProperty
    collider = ObjectProperty(None)

    # By default will draw a blue square. 
    def __init__(self,size=(16,16),pos=(0,0),colordata=(0,0,1,0,'rgba'),speed=1,shape=None,size_hint=(1,1),obstacle=False):
        super().__init__(size=size,pos=pos,colordata=colordata,shape=shape,size_hint=size_hint,obstacle=obstacle)
        self.transparentcolor = 0,0,0,0,'rgba'
        self.init_collider()        

    def init_collider(self):
        ##print('initializing collider')
        if self.collider != None:
            self.remove_widget(self.collider)
        self.collider = SimpleSprite(shape=self.shape,colordata=(1,0,0,1,'rgba'),speed=self.speed,size_hint = self.size_hint)
        self.add_widget(self.collider)

    def check_collision(self,widget,vector):
        newvector = vector
        c = self.collider
        c.speed = self.speed
        c.pos = self.pos
        c.size = self.size
        c.size_hint = (None,None)
        c.move(newvector)
        if (c.collide_widget(widget)):
            newvector = (0,vector[1])
            c.moveTo(self.pos)
            c.move(newvector)
            if (c.collide_widget(widget)):
                newvector = (vector[0],0)
                c.moveTo(self.pos)
                c.move(newvector)
                if (c.collide_widget(widget)):
                    newvector=(0,0)
                    c.moveTo(self.pos)
        c.moveTo(self.pos)                    
        return newvector
        

class Cell(SimpleSprite):
    def __init__(self,size=(16,16),pos=(0,0),colordata=(175/256,176/256,148/256,0,'rgba')):
        #print('Cell.__init__')
        super().__init__(size=size,pos=pos,colordata=colordata)


class Wall(SimpleSprite):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None)     

    def __init__(self,size=(16,16),pos=(0,0),colordata=(0,0,1,1,'rgba'),obstacle=True):
        super().__init__(size=size,pos=pos,colordata=colordata,obstacle=obstacle)
        self.blockVert = False
        self.blockHoriz = True        
          


class Floor(SimpleSprite):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None) 

    def __init__(self,size=(16,16),pos=(0,0),colordata=(0,0,1,1,'rgba'),obstacle=True):
        super().__init__(size=size,pos=pos,colordata=colordata,obstacle=obstacle)
        self.blockHoriz = False
        self.blockVert = True

class Ball(Sprite):
    id = ObjectProperty(None)
    def __init__(self,size=(16,16),pos=(0,0),colordata=(.75,0,0,1,'rgba'),size_hint=(None,None),speed = 1):
        super().__init__(shape=Ellipse(size=size,pos=pos),colordata=colordata,size_hint=size_hint,speed=speed)
        self.id='ball'


class Goal(SimpleSprite):  
    id = ObjectProperty(None)     

    def __init__(self,size=(16,16),pos=(0,0),colordata=(0,.75,0,1,'rgba'),size_hint=(None,None)):
        self.transparentcolor = 0,0,0,0,'rgba'
        super().__init__(size=size,pos=pos,colordata=self.transparentcolor,size_hint=size_hint)
        self.id='goal'
        self.add_widget(Label(text='EXIT',text_size=self.size,color=(0,.75,0,1)))
