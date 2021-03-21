KIVY_NO_ARGS=1
#kivy imports
import kivy
kivy.require('2.0.0')
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.logger import Logger, LOG_LEVELS
from kivy.app import App
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import (BooleanProperty, NumericProperty, BoundedNumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock

#plyer imports
from plyer import accelerometer, vibrator

#local imports
from ellermaze import EllerMaze
from ellermaze import EllerMazeGenerator
from controller import Controller
from mazesprites import (Cell, Wall, Floor, Ball, Goal)
from menu import GameMenu, PauseMenu
from sets import AssetSet

#system imports
import sys
import numpy as np
import random as rn
import threading as th
import concurrent.futures as cf

class MazeApp(App):
    def build(self):
        config = self.config
        loglevel = config['MazeApp']['loglevel']        #start logging before doing anything else
        Logger.setLevel(LOG_LEVELS[loglevel])        
        super().__init__()  
        opts = sys.argv                                                   
        game = MazeGame()
        game.start(config=config, opts=opts)
        return game

    def build_config(self, config):
        config.setdefaults('MazeApp', {
            'loglevel': 'info',
        })
        config.setdefaults('MazeGame', {
            'difficulty': 2,
            'interval': 0.12,
            'keyboard': False,
            'sound': True,
            'vibrate': True
        })        

# Cool colors:
#   175/256,176/256,148/256,1
#   .084, .098, .120, .9


class MazeGame(Widget):
    mazeGenerator = ObjectProperty(None)
    gridHeight = ObjectProperty(None)
    gridWidth = ObjectProperty(None)
    player1 = ObjectProperty(None)
    difficulty = BoundedNumericProperty(2, min=1, max=5)
    running = BooleanProperty(None)
    paused = BooleanProperty(None)
    playfield = ObjectProperty(None)
    loopEvent = ObjectProperty(None)
# ------------------------------------------------------
    def start(self,config = None, opts=[]):
        self.load_config_settings(config=config)
        self.load_opts_settings(opts=opts)
        self.player1 = Controller(rootWidget=self,useKeyboard=self.useKeyboard)
        self.playfield = Playfield()
        self.size = Window.size
        w = self.size[0]
        h = self.size[1]
        psize = (0,0)
        if w > h:
            psize = (h,h)
        else:
            psize = (w,w)
        self.playfield.size = psize
        bottom = 0
        left = int(w/2 - psize[0]/2)
        self.playfield.xoffset = left
        self.playfield.yoffset = bottom
        self.add_widget(self.playfield)
        self.set_signoff()
        self.end_game(victory=False)
# ------------------------------------------------------
    def load_config_settings(self, config):
        self.config = config 
        error = False
        try:
            difficulty = config.getint('MazeGame','difficulty')
        except Exception:
            Logger.debug('config for difficulty didn''t work')
            difficulty=2
            error = True
        try:
            interval = config.getfloat('MazeGame','interval')  
        except Exception:
            Logger.debug('config for interval didn''t work')    
            interval = 0.16
            error = True
        try:
            soundOn = config.getboolean('MazeGame','sound')  
        except Exception:
            Logger.debug('config for sound didn''t work')    
            soundOn = False
            error = True
        try:
            vibrateOn = config.getboolean('MazeGame','vibrate')  
        except Exception:
            Logger.debug('config for vibrate didn''t work')    
            vibrateOn = False 
            error = True
        try:
            useKeyboard = config.getboolean('MazeGame','keyboard')  
        except Exception:
            Logger.debug('config for keyboard didn''t work')    
            useKeyboard = False 
            error = True            
        self.difficulty = difficulty
        self.interval = interval
        self.soundOn = soundOn
        self.vibrateOn = vibrateOn 
        self.useKeyboard = useKeyboard           
        item = not error
        return item
# ------------------------------------------------------
    def set_signoff(self):
        roll = rn.randint(0,999999999999)
        if roll != 420:
            text = 'Goodbye!'
        else:
            text = 'Wake up, Neo'
        self.signoff = text
# ------------------------------------------------------
    def load_opts_settings(self,opts):
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        for opt in opts:
            if opt.startswith('-k'):    #keyboard active
                self.useKeyboard = True
            if opt.startswith('-d') or opt.startswith('--debug') :    #debug mode
                self.useKeyboard = 'True'
                Logger.setLevel(LOG_LEVELS["debug"])
            if opt.startswith('--nosound'):    
                self.soundOn = False
            if opt.startswith('--novibrate'):    
                self.vibrateOn = False
            if opt.startswith('--sound'):    
                self.soundOn = True 
            if opt.startswith('--vibrate'):    
                self.vibrateOn = True
# ------------------------------------------------------
    def new_game(self): # {'difficulty': difficulty, 'soundOn:': soundOn, 'vibrateOn': vibrateOn}
        result = self.hide_menu()
        Logger.debug('hide_menu={}'.format(result))
        self.difficulty = result['difficulty']
        self.soundOn = result['sound']
        self.vibrateOn = result['vibrate']
        self.set_config({'difficulty':self.difficulty,'sound':self.soundOn,'vibrate':self.vibrateOn})
        self.player1.enable()
        self.playfield.new_game(self.difficulty)
        Logger.debug('new_game: self={}'.format(self))
        # v = (0,0)
        # self.player1.set_vector(v=v)
        self.player1.touchWidget.activate(widget=self.playfield.ball)
        Window.bind(on_request_close=self._on_request_close)
        self.running = True
        self.schedule_next_update()
# ------------------------------------------------------
    def schedule_next_update(self):
        self.loopEvent = Clock.schedule_interval(self.update, self.interval)
# ------------------------------------------------------
    def cancel_next_update(self):
        try:
            self.loopEvent.cancel()
            return True
        except Exception:
            return False
# ------------------------------------------------------
    # back button on Android; Escape on Windows
    def _on_request_close(self, value, source=None):
        if source == 'keyboard':
            self.pause_game()
            Window.release_all_keyboards()
            return True
        else:
            return False        
# ------------------------------------------------------
    def update(self, dt):
        #Logger.debug('update: running={}'.format(self.running))
        if (self.running):
            self.running_update()
# ------------------------------------------------------
    def running_update(self):
        victory = self.playfield.update_game(player=self.player1)
        if victory:
            self.end_game(victory)
 # ------------------------------------------------------               
    def end_game(self, victory=True, menu=None):
        self.cancel_next_update()
        if victory:
            text = self.get_victory_text()
            delay = 1.5           #the delay is to allow time for the victory sound and animation
        else:
            text = 'Ready to begin?'
            delay = 0
        self.running = False
        self.player1.disable()
        self.set_config({'difficulty':self.difficulty,'sound':self.soundOn,'vibrate':self.vibrateOn})
        def callback(dt):
            self.show_menu(caption=text)
        if delay > 0:
            self.loopEvent = Clock.schedule_once(callback, delay)
        else:
            self.show_menu(caption=text)
# ------------------------------------------------------
    def set_config(self, values):
        for item in values:
            try:
                self.config.set('MazeGame',item,values[item])
            except Exception:
                Logger.debug('Could not set config {}'.format(item))
# ------------------------------------------------------
    def get_victory_text(self):
        values = ('Nice job!','You win!','Well Done!','Victory!','Success!', 'Outstanding!')
        r = rn.randrange(0, len(values))
        item = values[r]
        return item
# ------------------------------------------------------
    def quit(self):
        d = self.hide_menu()
        Logger.debug('config:{}'.format(d))
        self.set_config(d)
        self.config.write()
        print(self.signoff)
        sys.exit(0)
# ------------------------------------------------------
    def show_menu(self,caption):
        difficulty=self.difficulty
        soundOn=self.soundOn
        vibrateOn=self.vibrateOn
        self.gameMenu = GameMenu(difficulty=difficulty,caption=caption,soundOn=soundOn,vibrateOn=vibrateOn)
        self.gameMenu.size = Window.size
        def callback(value):
            self.new_game()
        self.gameMenu.newButton.bind(on_press=callback)
        def callback(value):
            self.quit()
        self.gameMenu.quitButton.bind(on_press=callback)
        self.add_widget(self.gameMenu)
# ------------------------------------------------------
    def hide_menu(self):
        difficulty = self.gameMenu.difficulty
        soundOn = self.gameMenu.soundOn
        vibrateOn = self.gameMenu.vibrateOn
        self.remove_widget(self.gameMenu)
        self.set_config({'difficulty':self.difficulty,'sound':self.soundOn,'vibrate':self.vibrateOn})
        return {'difficulty': difficulty, 'sound': soundOn, 'vibrate': vibrateOn}
# ------------------------------------------------------  
    def resume_game(self, menu):
        self.soundOn = menu.soundOn
        self.vibrateOn = menu.vibrateOn
        self.set_config({'sound':self.soundOn,'vibrate':self.vibrateOn})
        menu.parent.remove_widget(menu)
        self.player1.enable()
        self.running = True
        self.paused = False
        self.schedule_next_update() 
        Window.bind(on_request_close=self._on_request_close) 
# ------------------------------------------------------ 
    def pause_game(self):
        self.paused = True
        self.running = False
        self.cancel_next_update()
        Window.unbind(on_request_close=self._on_request_close)
        self.show_pause_menu()
# ------------------------------------------------------  
    def quit_game(self, menu=None):
        self.cancel_next_update()
        Logger.debug('Quitting game: self={}'.format(self)) 
        if menu != None:
            self.soundOn = menu.soundOn
            self.vibrateOn = menu.vibrateOn
            self.set_config({'difficulty':self.difficulty,'sound':self.soundOn,'vibrate':self.vibrateOn})
            menu.parent.remove_widget(menu)
        self.end_game(victory=False)                       
# ------------------------------------------------------
    def show_pause_menu(self,caption='Game Paused'):
        menu = PauseMenu(caption=caption,soundOn=self.soundOn,vibrateOn=self.vibrateOn)
        menu.size = Window.size
        def callback(value):
            self.resume_game(menu=value.parent)
        menu.resButton.bind(on_press=callback)
        def callback(value):
            self.quit_game(menu=value.parent)   #quit to main menu
        menu.mainButton.bind(on_press=callback)
        def callback(value):
            self.quit()
        menu.quitButton.bind(on_press=callback)
        self.add_widget(menu)
        self.loopEvent.cancel
        return False
# ######################################################
class Playfield(FloatLayout):
    topLeft = ObjectProperty(None)
    bottomLeft = ObjectProperty(None)
    topRight = ObjectProperty(None)
    bottomRight = ObjectProperty(None)
    ball = ObjectProperty(None)
    start = ObjectProperty(None)
    end = ObjectProperty(None)
    gameMenu = ObjectProperty(None)
    mazeSize = ObjectProperty(None)
    mazePos = ObjectProperty(None)

    def __init__(self,*args,backColor=Color(32/256, 32/256, 43/256, .55),cellColor=Color(0,0,0,0),wallColor=Color(0,0,1,1),ballColor=Color(.7,0,0,1),goalColordata=[0,.8,0,1],xoffset = 32,yoffset = 24):
        super().__init__()
        #print('Playfield.__init__')
        self.backColor = backColor
        self.cellColor = cellColor
        self.wallColor = wallColor
        self.ballColor = ballColor
        self.goalColordata = goalColordata
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.cornerVar = -1     #this tells choose_corners to start with option 4 for the first game
        self.mazeSize = self.size
        self.mazePos = self.pos
        with self.canvas.before:
            self.color = backColor
            self.rect = Rectangle(pos=self.mazePos,size=self.mazeSize)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.assets = AssetSet()
# ------------------------------------------------------
    def update_canvas(self,instance,value): 
        self.update_rect()    
# ------------------------------------------------------
    def update_rect(self):
        self.rect.pos = self.mazePos
        self.rect.size = self.mazeSize 
 # ------------------------------------------------------ 
    def new_game(self,difficulty):
        self.assetData = self.assets.get_next()   
        dm = self.get_grid_size(difficulty)
        mg = EllerMazeGenerator(dm[0], dm[1])
        self.draw_maze(mg.GetMaze())
        self.place_goal(self.end)
        self.place_ball(cell=self.start,difficulty=difficulty)          
 # ------------------------------------------------------ 
    def update_game(self, player):
        self.move_sprite(player,self.ball) 
        if not self.ball.moving:
            player.set_vector = (0,0)   
        victory = self.check_victory(self.ball,self.goal)   
        return victory    
# ------------------------------------------------------
    def get_grid_size(self,difficulty):
        switcher = {
            1: (6,6),
            2: (8,8),
            3: (10,10),
            4: (14,14),
            5: (16,16)
            }
        item = switcher.get(difficulty,(12,12))
        return item
 # ------------------------------------------------------   
    def draw_maze(self,maze):
        self.clear_maze()
        mtrx = maze.ToArray()
        w = mtrx.shape[0]  #number of cells wide
        h = mtrx.shape[1] #number of cells high
        cw = int(self.width / (w + 1))
        ch = int(self.height / (h + 1))
        self.wallSize = (int(cw/5),ch)    #ch + int(ch/5)
        self.floorSize = (cw,int(ch/5))
        self.walls = []
        self.floors = []
        for y in range (h):
            for x in range (w):
                #add a blank cell to the layout
                invy = h-y    #because kivy puts 0,0 on bottom left
                c = Cell(pos=((x*cw)+self.xoffset,(invy*ch)-self.yoffset), size=(cw,ch),color=self.cellColor)
                self.add_widget(c)
                #look up the grid position and see if we need to add a wall and/or floor to the cell
                if (mtrx[x,y,1]):
                    item = Floor(pos=(c.pos[0]+2,c.pos[1]),size=(cw,int(ch/5)),source=self.assetData['floor'])
                    c.add_widget(item)   
                    self.floors.append(item)                
                if (mtrx[x,y,0]):
                    item = Wall(pos=c.pos,size=(int(cw/5),int(ch + int(ch/5))),source=self.assetData['wall']) 
                    c.add_widget(item)
                    self.walls.append(item)
        self.wallSize = self.walls[0].size
        self.floorSize = self.floors[0].size
        self.bottomRight = self.children[1]
        self.bottomLeft = self.children[w-1]
        self.topLeft = self.children[(w-1)*h-1]
        self.topRight = self.children[(w-2)*h+1] 
        self.draw_background()
        (self.start,self.end) = self.select_corners()
# ------------------------------------------------------
    def draw_background(self):
        last = len(self.children) - 1
        pos = self.bottomLeft.children[0].pos
        self.mazePos = pos
        w = self.children[0].children[0].pos[0] - pos[0]
        item = self.topLeft.children[0]
        h = item.pos[1] 
        size = (w,h)
        self.mazeSize = size
        #Logger.debug('{}:pos={}  size={}'.format(self,pos,size))
        background = Image(source=self.assetData['background'], allow_stretch=True, keep_ratio=False, size=size, pos=pos, size_hint=(None,None))
        self.add_widget(background, last + 1)   #add to end so it's displayed on the bottom
        self.update_rect
# ------------------------------------------------------
    def select_corners(self):    
        if (self.cornerVar < 0):
            n = 1
        else:
            n = rn.randint(1,2)
        switcher = {1: (self.topRight, self.bottomLeft),
                    2: (self.topLeft, self.bottomRight)}        
        item = switcher.get(n,(self.topRight, self.bottomLeft))  
        self.cornerVar = n 
        return item          
# ------------------------------------------------------
    def clear_maze(self):
        self.clear_widgets()
        self.walls = []
        self.floors = []        
# ------------------------------------------------------
    def place_ball(self,cell,difficulty):
        x = cell.pos[0] + int(cell.size[0] / 2) - 6
        y = cell.pos[1] + int(cell.size[1] / 2) - 8
        width = int(cell.size[0] * .5) - 2
        height = int(cell.size[1] * .5) - 2
        speed = int(width / 3) + int(difficulty/2) + 2
        if speed <= 2:
            speed = 2
        Logger.debug('place_ball: speed={}'.format(speed))
        asset = self.assetData['ball']
        self.ball = Ball(speed=speed,size_hint=(None,None),source=asset[0],size=(width,height),pos=(x,y),allow_stretch=True,altSources=[asset[1]])
        self.ball.soundOn = self.parent.soundOn
        if self.parent.soundOn:
            soundAsset = 'assets/qubodup-bowling_roll-nofadeout.wav'        
            self.ball.add_sound(key='move', source = soundAsset)
            soundAsset = 'assets/ball-drop2.wav'
            self.ball.add_sound(key='win', source = soundAsset)
            soundAsset = 'assets/ball-hit1.wav'
            self.ball.add_sound(key='hit', source = soundAsset)        
        cell.add_widget(self.ball)
# ------------------------------------------------------
    def place_goal(self,cell):
        w = int(self.floorSize[0] / 2)
        h = w
        x = cell.pos[0] + (w / 2) + (self.wallSize[0] / 2)
        y = cell.pos[1] - (h / 2)
        #.debug('place_goal: y={}   cell.pos={}'.format(y,cell.pos))
        src = self.assetData['goal_bottom']
        Logger.debug(src)
        self.goal = Goal(pos=(x,y),size=(w,h), source=src, allow_stretch=True, keep_ratio = True)
        cell.add_widget(self.goal)
        for item in (self.floors):
            if item.collide_widget(self.goal) and item.pos[0] <= self.goal.pos[0]:
                item.obstacle = False
                item.parent.remove_widget(item)
                self.floors.remove(item)
                break
        self.goal.flash()
# ------------------------------------------------------
    def check_victory(self,sprite,goal):
        item = sprite.collide_widget(goal)
        if item:
            self.celebrate_victory(sprite,goal)
        return item  
# ------------------------------------------------------
    def celebrate_victory(self,sprite,goal):
        x = goal.pos[0] + 6
        y = sprite.pos[1]
        sprite.moveTo((x,y))
        def callback(dt):
            sprite.move(vector=(0,-1))
        for i in range(0,9):
            Clock.schedule_once(callback, i * 0.16)
        with cf.ThreadPoolExecutor() as executor:            
            flashThread = executor.submit(goal.flash)
            if self.parent.soundOn:
                soundThread = executor.submit(self.ball.start_sound, 'win')

            if self.parent.vibrateOn:
                try:
                    vibeThread = executor.submit(vibrator.vibrate,.018)
                except NotImplementedError:
                    Logger.debug('Vibrate not working')                
# ------------------------------------------------------                      
    def move_sprite(self,player,sprite):
        v = player.get_vector()
        o = self.walls + self.floors
        sprite.move(vector=v, obstacles=o)  #we have to call the move method even if vector is 0,0 so ball will stop rolling when it's not moving.

