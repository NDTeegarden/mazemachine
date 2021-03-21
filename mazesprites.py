from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import BooleanProperty, NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.clock import Clock

import concurrent.futures as cf

class SimpleSprite(Widget):
    color = ObjectProperty(None)
    shape = ObjectProperty(None)
    speed = ObjectProperty(None)
# ------------------------------------------------------    
    def set_variables(self,size,pos,color,speed,shape,size_hint,obstacle):
        self.obstacle = obstacle
        self.speed = speed
        self.color = color
        self.size_hint = size_hint
        if shape != None:
            try:
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
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,0,0),speed = 1,shape=None,size_hint = (1,1),obstacle=False):
        super().__init__()
        self.set_variables(size=size,pos=pos,color=color,speed=speed,shape=shape,size_hint=size_hint,obstacle=obstacle)
        self.init_canvas()
        self.post_init()
# ------------------------------------------------------
    def post_init(self):
        pass        
# ------------------------------------------------------
    def init_canvas(self):
        self.canvas.clear()
        self.canvas.add(self.color)
        self.canvas.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)        
# ------------------------------------------------------
    def update_canvas(self, *args):
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
    def move(self,vector,speed=0):
        if speed == 0:
            speed = self.speed
        if (vector != (0,0)) and (speed != 0):
            try:
                dx = vector[0] * speed
                dy = vector[1] * speed
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
class Cell(SimpleSprite):
# ------------------------------------------------------
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,0,0)):
        super().__init__(size=size,pos=pos,color=color)
      
# ######################################################
class Sprite(Image):
    transparentcolor = ObjectProperty(None) 
    speed = ObjectProperty(None)
    collider = ObjectProperty(None)
    moving = ObjectProperty(None)
# ------------------------------------------------------
    def __init__(self,source,pos,size,size_hint=(None,None),allow_stretch=False,keep_ratio=True,speed=1,altSources=[], soundOn=True, **kwargs):
        super().__init__(size=size,pos=pos,source=source,allow_stretch=allow_stretch, keep_ratio=keep_ratio,**kwargs)
        self.sources = altSources
        self.sources.insert(0,source)
        self.load_content()
        self.transparentcolor = Color(0,0,0,0)
        self.speed = speed
        self.soundOn = soundOn
        self.sounds = {}
        self.init_collider()  
        self.init_image_animation() 
#------------------------------------------------------
    def load_content(self):
        l = len(self.sources)
        if l > 1:
            #force program to load all images we will eventually use
            for i in range(1,l-1):
                self.source = self.sources[i]    
            self.source = self.sources[0]     
#------------------------------------------------------
    def add_sound(self,key,source):
        s = None
        try:
            s = SoundLoader.load(source)
        except Exception:
            import traceback
            traceback.print_exc()
            status = '{}: Failed to load sound {}'.format(self,source)
            Logger.warning(status)
        if s != None:
            self.sounds[key] = s      
# ------------------------------------------------------
    def set_animation(self, index):
        if index >= len(self.sources):
            index = 0
        self.source = self.sources[index]
#------------------------------------------------------
    def init_image_animation(self):
        self.moving = False
        self.anim_delay = -1
        self.anim_loop = 0 
# ------------------------------------------------------
    def start_animating(self):
        if self.anim_delay < 0:
            self.anim_delay = .16
            self.anim_loop = 0            
# ------------------------------------------------------
    def stop_animating(self):
        if self.anim_delay != -1:
            self.anim_delay = -1
# ------------------------------------------------------
    def start_sound(self, key='move', volume=1):
        if self.soundOn:
            s = self.sounds[key]
            Logger.debug('start_sound {}: {}'.format(key,s.state))
            if s != None and s.state != 'play':
                try:
                    s.volume = volume
                    s.play()
                except Exception:
                    Logger.debug('Sound {} not working'.format(key))
# ------------------------------------------------------
    def stop_sound(self, key='move'):
        s = self.sounds[key]
        Logger.debug('stop_sound {}: {}'.format(key, s.state))
        if s != None and s.state == 'play':
            try:
                s.stop()
            except Exception:
                Logger.debug('Unable to stop sound {}'.format(key))
            
# ------------------------------------------------------
    def init_collider(self):
        if self.collider != None:
            self.remove_widget(self.collider)
        self.collider = SimpleSprite(color=self.transparentcolor,speed=self.speed,size_hint=self.size_hint)
        self.collider.pos = self.pos #((self.pos[0]+4),(self.pos[1]+4))
        self.collider.size = self.size #((self.size[0]-4),(self.size[1]-4))
        self.add_widget(self.collider)
# ------------------------------------------------------        
    def move(self,vector,obstacles=[]):
        if vector == (None,None):
            return
        if vector == (0,0):
            self.moving = False
            self.stop_animating()
            #self.stop_sound('move')
            return
        else:
            # multiply vector times speed
            s = self.speed
            dx = vector[0] * s
            dy = vector[1] * s
            adjvector = (dx,dy)
            # check for obstacles - in a separate thread to keep Android OS happy
            with cf.ThreadPoolExecutor() as executor:
                future = executor.submit(self.get_new_pos,adjvector,obstacles)
            result = future.result()
            newpos = result[0]
            colFlag = result[1]
            # if colFlag:
            #     self.start_sound('hit')
            #Logger.debug('move: newpos={}'.format(newpos))
        # handle animation if any            
        if (newpos != self.pos):
            self.select_animation(vector)
            self.moveTo(newpos)
            self.collider.moveTo(newpos)
            self.moving = True
            with cf.ThreadPoolExecutor() as executor:
                animThread = executor.submit(self.start_animating)
            #self.start_sound('move')
        else:
            self.moving = False
            self.stop_animating()
            # self.start_sound('hit')
            #self.stop_sound('move')
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)
# ------------------------------------------------------
    def get_new_pos(self, vector, obstacles):
        oldx = self.pos[0]
        oldy = self.pos[1]
        dx = int(vector[0])
        dy = int(vector[1])
        newx = oldx + dx
        newy = oldy + dy
        c = self.collider
        c.moveTo(pos=(newx,newy))
        collisions = self.get_collisions(widget=c, obstacles=obstacles)
        flag = False
        if len(collisions) > 0:
            flag = True
            if (dx != 0):                
                newx = oldx + dx
                newy = oldy  
                c.moveTo(pos=(newx,newy))
                newlist = self.get_collisions(widget=c, obstacles=collisions)
                if len(newlist) == 0:
                    collisions = newlist 
            if (dy != 0) and len(collisions) > 0:
                newx = oldx
                newy = oldy + dy
                c.moveTo(pos=(newx,newy))
                newlist = self.get_collisions(widget=c, obstacles=collisions)
                if len(newlist) == 0:
                    collisions = newlist 
            if len(collisions) > 0:
                newx = oldx
                newy = oldy
        newpos = (int(newx), int(newy))
        return (newpos, flag)
# ------------------------------------------------------
    def get_collisions(self, widget, obstacles):
        collisions = []
        for item in obstacles:
            if widget.collide_widget(item):
                collisions.append(item)
        return collisions       
# ------------------------------------------------------
    def select_animation(self, vector):
        if len(self.sources) > 1:
            if (vector[0] < 0) or (vector[1] > 0):
                self.set_animation(0)   # left or up
            else:
                self.set_animation(1)   # right or down
# ------------------------------------------------------                
    def decrement_vector(self, vector):
        newx = vector[0]
        newy = vector[1]
        #Logger.debug('before decrementing: newx={}  newy={}'.format(newx,newy))
        if newx <= -1:
            newx = newx + 1
        elif newx >= 1:
            newx = newx - 1
        else:
            newx = 0
        if newy <= -1:
            newy = newy + 1
        elif newy >= 1:
            newy = newy - 1
        else:
            newy = 0
        #Logger.debug('after decrementing: newx={}  newy={}'.format(newx,newy))            
        newvector = (newx,newy)
        return newvector
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
        self.anim_delay = .25     

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
        self.anim_delay = .25

# ######################################################
class Ball(Sprite):
    id = ObjectProperty(None)
    def __init__(self,size_hint=(None,None),speed = 2,pos=(0,0), size=(16,16),source=None,**kwargs):
        super().__init__(size_hint=size_hint,speed=speed,pos=pos,size=size,source=source,**kwargs)
        self.id='ball'
        self.anim_delay = -1

# ######################################################
class Goal(Image):  
    id = ObjectProperty(None)
    def __init__(self, size=(16,16),pos=(0,0), source=None, allow_stretch=True, keep_ratio = True):
        super().__init__(size=size,pos=pos,source=source,allow_stretch=allow_stretch, keep_ratio=keep_ratio)
        self.id='goal'
        self.anim_delay = -1
    
    def flash(self, anim_loop = 4, anim_delay = 0.36):
        self.anim_delay = anim_delay
        self.anim_loop = anim_loop




          

