from kivy.uix.widget import Widget
from kivy.uix.image import Image
#from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.clock import Clock

class SimpleSprite(Widget):
    color = ObjectProperty(None)
    shape = ObjectProperty(None)
    speed = ObjectProperty(None)
# ------------------------------------------------------    
    def set_variables(self,size,pos,color,speed,shape,size_hint,obstacle):
        #print('Cell.set_variables')
        self.obstacle = obstacle
        self.speed = speed
        self.color = color
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
# ------------------------------------------------------
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,0,0),speed = 1,shape=None,size_hint = (1,1),obstacle=False,image=None):
        #print('Cell.__init__')
        super().__init__()
        self.set_variables(size=size,pos=pos,color=color,speed=speed,shape=shape,size_hint=size_hint,obstacle=obstacle)
        #print(self.color)
        self.init_canvas()
        self.post_init()
# ------------------------------------------------------
    def post_init(self):
        #print('Cell.post_init')
        pass        
# ------------------------------------------------------
    def init_canvas(self):
        #print('Cell.init_canvas')
        self.canvas.clear()
        self.canvas.add(self.color)
        self.canvas.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)        
# ------------------------------------------------------
    def update_canvas(self,*args):
        #print(self,'.update_canvas')
        try:
            self.update_shape()
        except Exception:
            print('sprite',self,'failed to update_shape')       
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def move(self,vector):
        ##print('moving with vector',vector)
        if (vector != (0,0)):
            s = self.speed
            try:
                dx = vector[0] * s
                dy = vector[1] * s
            except Exception:
                dx = 0
                dy = 0
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            self.pos = (x,y)
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)                             
        
# ######################################################
class Sprite(SimpleSprite):
    transparentcolor = ObjectProperty(None) 
    speed = ObjectProperty
    collider = ObjectProperty(None)
# ------------------------------------------------------
    # By default will draw a blue square. 
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,1,0),speed=1,shape=None,size_hint=(1,1),obstacle=False):
        super().__init__(size=size,pos=pos,color=color,speed=speed,shape=shape,size_hint=size_hint,obstacle=obstacle)
        self.transparentcolor = Color(0,0,0,0)
        self.init_collider()        
# ------------------------------------------------------
    def init_collider(self):
        ##print('initializing collider')
        if self.collider != None:
            self.remove_widget(self.collider)
        self.collider = SimpleSprite(shape=self.shape,color=Color(1,0,0,1),speed=self.speed,size_hint = self.size_hint)
        self.add_widget(self.collider)
# ------------------------------------------------------
    def check_collision(self,widget,vector):
        newvector = vector
        if not newvector == (0,0):
            c = self.collider
            c.speed = self.speed
            c.pos = self.pos
            c.size = self.size
            #c.size_hint = (None,None)
            c.move(newvector)
            if (c.collide_widget(widget)):
                #print('colllision with',widget,'using vector',newvector)
                newvector = (0,vector[1])
                c.moveTo(self.pos)
                c.move(newvector)
                if (c.collide_widget(widget)):
                    #print('colllision with',widget,'using vector',newvector)
                    newvector = (vector[0],0)
                    c.moveTo(self.pos)
                    c.move(newvector)
                    if (c.collide_widget(widget)):
                        #print('colllision with',widget,'using vector',newvector)
                        newvector=(0,0)
                        c.moveTo(self.pos)
                #print('newvector is',newvector)
            c.moveTo(self.pos)                    
        return newvector
# ------------------------------------------------------        
# ######################################################
class Cell(SimpleSprite):
    def __init__(self,size=(16,16),pos=(0,0),color=Color(175/256,176/256,148/256,0)):
        #print('Cell.__init__')
        super().__init__(size=size,pos=pos,color=color)
# ------------------------------------------------------
# ######################################################
class Wall(Image):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None)     
# ------------------------------------------------------
    def __init__(self,size=(3,15),pos=(0,0),source=None,allow_stretch=True,keep_ratio=False,obstacle=True):
        super().__init__(source=source,pos=pos,size=size,allow_stretch=allow_stretch,keep_ratio=keep_ratio)
        self.obstacle = obstacle
        self.blockVert = False
        self.blockHoriz = True        

# ######################################################
class Floor(Image):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None) 
# ------------------------------------------------------
    def __init__(self,size=(15,13),pos=(0,0),source=None,allow_stretch=True,keep_ratio=False,obstacle=True):
        super().__init__(source=source,pos=pos,size=size,allow_stretch=allow_stretch,keep_ratio=keep_ratio)
        self.obstacle = obstacle
        self.blockHoriz = False
        self.blockVert = True

# ######################################################
class Ball(Sprite):
    id = ObjectProperty(None)
    def __init__(self,size=(16,16),pos=(0,0),color=Color(.75,0,0,1),size_hint=(None,None),speed = 2):
        super().__init__(shape=Ellipse(size=size,pos=pos),color=color,size_hint=size_hint,speed=speed)
        self.id='ball'

# ######################################################
class Goal(Image):  
    id = ObjectProperty(None)
    def __init__(self, *args):
        super().__init__()
        self.id='goal'
        self.anim_delay = -1
    
    def flash(self, anim_loop = 20, anim_delay = 0.10):
        self.anim_delay = anim_delay
        self.anim_loop: anim_loop


          

