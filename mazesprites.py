from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import BooleanProperty, NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.clock import Clock
import traceback
import concurrent.futures as cf
from kivy.utils import platform
if platform == 'android':
    from androidaudio import AndroidAudioClip as AudioClip
else:
    from genericaudio import GenericAudioClip as AudioClip

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
    moving = BooleanProperty(None)
    soundOn = BooleanProperty(None)
# ------------------------------------------------------
    def __init__(self,source,pos,size,size_hint=(None,None),allow_stretch=False,keep_ratio=True,speed=1,altSources=[], soundSources={}, soundOn=False, **kwargs):
        super().__init__(size=size,pos=pos,source=source,allow_stretch=allow_stretch, keep_ratio=keep_ratio,**kwargs)
       #Logger.debug('READ THIS: pos={}'.format(pos))
       #Logger.debug('READ THIS: Vector(self.pos)={}'.format(Vector(self.pos)))
        self.sources = altSources
        self.sources.insert(0,source)
        self.soundOn = soundOn
        self.soundSources= soundSources
        self.sounds = {}
        self.load_content()
        self.transparentcolor = Color(0,0,0,0)
        self.speed = speed
        self.init_collider()  
        self.init_image_animation() 
        def callback(instance, value):
            if not value:
                self.pause_all_sounds()
            else:     #load sounds if they were never loaded (for example if player starts with sound off but later turns it on)
                if len(self.sounds) == 0:
                    self.load_sounds()
                self.handle_move_sound(self, self.moving)
        self.bind(soundOn=callback)
#------------------------------------------------------
    def load_content(self):
        self.load_images()
        self.load_sounds()
#------------------------------------------------------
    def load_images(self):
        l = len(self.sources)
        if l > 1:
            #force program to load all images we will eventually use
            for i in range(1,l-1):
                self.source = self.sources[i]    
            self.source = self.sources[0]
#------------------------------------------------------
    def load_sounds(self):
        l = len(self.soundSources)
        if l > 0 and self.soundOn:
            #force program to load all sounds we will eventually use
            for key in self.soundSources:
                source = self.soundSources[key]
                if key =='move':
                    self.add_move_sound(source=source, key=key)
                elif key == 'win':
                    self.add_victory_sound(source=source, key=key)
                else:
                    self.add_sound(source=source,key=key)
#------------------------------------------------------
    def add_sound(self,key,source, loop=False):
        if (key not in self.soundSources) or (self.soundSources[key] != source):
            self.soundSources[key] = source
        item = True
        try:
            sound = AudioClip(source=source,loop=loop)
        except Exception:
            item = False
            traceback.print_exc()
            Logger.debug('could not add sound {}'.format(source))             
        if item:
            self.sounds[key] = sound
        return item
#------------------------------------------------------
    def add_sound_source(self,key,source, loop=False):
        item = True
        try:
            self.soundSources[key] = source
        except Exception:
            item = False
            traceback.print_exc()
            Logger.debug('could not add sound source {}'.format(source)) 
        return item        
#------------------------------------------------------
    def add_move_sound(self,source, key='move', loop=True):
        Logger.debug('Loading move sound {}'.format(key))
        if (key not in self.soundSources) or (self.soundSources[key] != source):
            self.soundSources[key] = source        
        item = True
        try: 
            sound = AudioClip(source=source, loop=loop)
        except Exception:
            item = False
            traceback.print_exc()
            Logger.debug('could not add sound {}'.format(source))            
        if item:
            self.sounds[key] = sound
            self.bind(moving=self.handle_move_sound)
        return item
# ------------------------------------------------------
    def handle_move_sound(self,instance,value):
        if self.soundOn:
            item = True
            try:
                sound = self.sounds['move']
            except Exception:
                traceback.print_exc()
                item = False
            moving = value
            #Logger.debug('READ THIS: handle_move_sound: moving={}  playing={}'.format(moving,sound.isPlaying()))
            if item and moving and (not sound.isPlaying()):
                sound.play()
            elif item and (not moving) and sound.isPlaying():
                sound.pause()
       
#------------------------------------------------------
    def add_victory_sound(self,source, key='win', loop=False):
        Logger.debug('Loading victory sound {}'.format(key))
        if (key not in self.soundSources) or (self.soundSources[key] != source):
            self.soundSources[key] = source        
        item = True
        try: 
            sound = AudioClip(source=source, loop=loop)
        except Exception:
            item = False
            traceback.print_exc()
            Logger.debug('could not add sound {}'.format(source))            
        if item:
            self.sounds[key] = sound
        return item            
# ------------------------------------------------------
    def handle_victory_sound(self):
        # if there's a move sound, try to stop it, then release it.
        item = True
        try:
            sound = self.sounds['move']  
        except Exception:
            item = False
        if item:
            try:
               sound.stop()
            except Exception:
                pass
            try:
                sound.release()
            except Exception:
                pass
        # remove the binding on moving - even if there's no stop sound defined     
        try:
            self.unbind(moving=self.handle_move_sound)
        except Exception:
            pass
        # now play the victory sound (if there is one, and sound is on)
        item = True 
        if self.soundOn:
            try:
                sound = self.sounds['win']
            except Exception:
                item = False
                traceback.print_exc()
                return item
            if item:
                Logger.debug('READ THIS: trying to play victory sound {}'.format(sound))
                try:
                    sound.play()
                except Exception:
                    Logger.debug('FAILED!: Failed')
                    traceback.print_exc()
                    item = False
        return item
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
    def start_sound(self, key='move'):
        if self.soundOn:
            s = self.sounds[key]
            if s != None:
                if s.isPlaying():
                    try:
                        s.play()
                    except Exception:
                        Logger.debug('Sound {} not working'.format(key))
# ------------------------------------------------------
    def stop_sound(self, key='move'):
        s = self.sounds[key]
        if s != None:
            if s.isPlaying():
                try:
                    s.stop()
                except Exception:
                    Logger.debug('Unable to stop sound {}'.format(key))
# ------------------------------------------------------
    def pause_sound(self, key='move'):
        s = self.sounds[key]
        if s != None:
            try:
                s.pause()
            except Exception:
                Logger.debug('Unable to stop sound {}'.format(key))
# ------------------------------------------------------
    def pause_all_sounds(self):
        for key in self.sounds:
            if key != 'win':
                s = self.sounds[key]
                if s != None:
                    try:
                        s.pause()
                    except Exception:
                        Logger.debug('Unable to pause sound {}'.format(key))
                       
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
        if vector == (0,0) or vector == (None,None):
            self.moving = False
            self.stop_animating()
            return
        else:
            (oldx,oldy) = self.pos
            oldpos=(oldx,oldy)
           #Logger.debug('READ THIS: self.pos={}  oldpos={}'.format(self.pos,oldpos))
            # multiply vector times speed
            s = self.speed
            dx = vector[0] * s
            dy = vector[1] * s
            adjvector = (dx,dy)
            #Logger.debug('READ THIS: adjusted-vector={}'.format(adjvector))
            # check for obstacles - in a separate thread to keep Android OS happy
            with cf.ThreadPoolExecutor() as executor:
                future = executor.submit(self.get_new_pos,adjvector,obstacles)
            result = future.result()
            newpos = result
        # handle animation if any            
        if (newpos != oldpos):
            #Logger.debug('READ THIS: newpos != oldpos | newpos={} oldpos={} colFlag={}'.format(newpos,oldpos,colFlag))
            self.select_animation(vector)
            self.moveTo(newpos)
            self.collider.moveTo(newpos)
            self.moving = True
            with cf.ThreadPoolExecutor() as executor:
                animThread = executor.submit(self.start_animating)
        else:
            self.moving = False
            self.stop_animating()
        #Logger.debug('READ THIS: newpos={} oldpos={} colFlag={}'.format(newpos,oldpos,colFlag))
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)
# ------------------------------------------------------
    def get_new_pos(self, vector, obstacles):
        newpos = self.pos
        dx = int(vector[0])
        dy = int(vector[1])
        newvector = (dx,dy)
        while (newvector != (0,0)) and (newpos == self.pos):
            newpos= self.test_with_vector(newvector, obstacles)
            flag = (newpos == self.pos)
            if flag and dx != 0:
                if dx > 1:
                    dx = dx - 1
                elif dx < 1:
                    dx = dx + 1
                else:
                    dx = 0
            if flag and dy != 0:
                if dy > 1:
                    dy = dy -1
                elif dy < 1:
                    dy = dy + 1
                else:
                    dy = 0 
        return (newpos)
# ------------------------------------------------------
    def test_with_vector(self, vector, obstacles):
        (oldx, oldy) = self.pos
        (dx,dy) = vector
        newx = oldx + dx
        newy = oldy + dy
        c = self.collider
        c.moveTo(pos=(newx,newy))
        collisions = self.get_collisions(widget=c, obstacles=obstacles)
        if len(collisions) > 0:
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
        return (newpos)              
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
        self.anim_delay = .20     

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
    
    def flash(self, anim_loop = 4, anim_delay = 0.32):
        self.anim_delay = anim_delay
        self.anim_loop = anim_loop




          

