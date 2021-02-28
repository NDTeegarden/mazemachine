KIVY_NO_ARGS=1
#kivy imports
import kivy
kivy.require('2.0.0')
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.logger import Logger, LOG_LEVELS
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import (BooleanProperty, NumericProperty, BoundedNumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock

#plyer imports
from plyer import accelerometer

#local imports
from ellermaze import EllerMaze
from ellermaze import EllerMazeGenerator
from humint import HumInt
from mazesprites import (Cell, Wall, Floor, Ball, Goal)
from menu import GameMenu
from sets import AssetSet

#system imports
import sys
import numpy as np
import random as rn


class MazeApp(App):
    def build(self):
        super().__init__()
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        useKeyboard = False
        for opt in opts:
            if opt.startswith('-k'):
                useKeyboard = True
        game = MazeGame()
        game.start(useKeyboard=useKeyboard)
        return game

# Cool colors:
#   175/256,176/256,148/256,1
#   .084, .098, .120, .9


class MazeGame(Widget):
    Logger.setLevel(LOG_LEVELS["debug"])
    mazeGenerator = ObjectProperty(None)
    gridHeight = ObjectProperty(None)
    gridWidth = ObjectProperty(None)
    player1 = ObjectProperty(None)
    difficulty = BoundedNumericProperty(3, min=1, max=5)
    running = BooleanProperty(None)
    playfield = ObjectProperty(None)
    loopEvent = ObjectProperty(None)
# ------------------------------------------------------
    def start(self,useKeyboard = False):
        self.player1 = HumInt(rootWidget=self,useKeyboard=useKeyboard)
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
        self.difficulty = 3
        self.end_game(victory=False)
# ------------------------------------------------------
    def new_game(self):
        self.difficulty = self.hide_menu()
        self.playfield.new_game(self.difficulty)
        self.running = True
        self.loopEvent = Clock.schedule_interval(self.update, 1.0 / 60.0)
# ------------------------------------------------------
    def update(self, dt):
        if (self.running):
            self.running_update()
# ------------------------------------------------------
    def running_update(self):
        self.playfield.move_sprite(self.player1,self.playfield.ball)   
        victory = self.playfield.check_victory(self.playfield.ball,self.playfield.goal)  
        if victory:
            self.end_game(victory)
 # ------------------------------------------------------               
    def end_game(self, victory=True):
        try:
            self.loopEvent.cancel()
        except Exception:
            pass
        finally:
            if victory:
                text = self.get_victory_text()
            else:
                text = 'Ready to begin?'
            self.running = False
            self.show_menu(difficulty=self.difficulty, caption=text)
# ------------------------------------------------------
    def get_victory_text(self):
        values = ('Nice job!','You win!','Well Done!','Victory!','Success!')
        r = rn.randrange(0, len(values))
        item = values[r]
        return item
# ------------------------------------------------------
    def quit(self):
        d = self.hide_menu()
        print('Goodbye!')
        sys.exit(0)
# ------------------------------------------------------
    def show_menu(self,difficulty,caption):
        self.gameMenu = GameMenu(difficulty=difficulty,caption=caption)
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
        self.remove_widget(self.gameMenu)
        return difficulty          
# ------------------------------------------------------                  

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
    def update_canvas(self,*args): 
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
    def get_grid_size(self,difficulty):
        switcher = {
            1: (7,7),
            2: (9,9),
            3: (12,12),
            4: (14,14),
            5: (18,18)
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
        self.wallSize = (0,0)
        self.floorSize = (0,0)
        self.walls = []
        self.floors = []
        for y in range (h):
            for x in range (w):
                #add a blank cell to the layout
                invy = h-y    #because kivy puts 0,0 on bottom left
                c = Cell(pos=((x*cw)+self.xoffset,(invy*ch)-self.yoffset), size=(cw,ch),color=self.cellColor)
                self.add_widget(c)
                #look up the grid position and see if we need to add a wall and/or floor to the cell
                if (mtrx[x,y,0]):
                    item = Wall(pos=c.pos,size=(int(cw/5),int(ch + int(ch/5))),source=self.assetData['wall']) 
                    c.add_widget(item)
                    self.walls.append(item)
                if (mtrx[x,y,1]):
                    item = Floor(pos=c.pos,size=(cw,int(ch/5)),source=self.assetData['floor'])
                    c.add_widget(item)   
                    self.floors.append(item)
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
        Logger.debug('{}:pos={}  size={}'.format(self,pos,size))
        background = Image(source=self.assetData['background'], allow_stretch=True, keep_ratio=False, size=size, pos=pos, size_hint=(None,None))
        self.add_widget(background, last + 1)   #add to end so it's displayed on the bottom
        self.update_rect
# ------------------------------------------------------
    def select_corners(self):    
        n = rn.randint(2,4)
        if (n == self.cornerVar) or (self.cornerVar < 0):
            n = 1
        switcher = {1: (self.topRight, self.bottomLeft),
                    2: (self.topLeft, self.bottomRight),
                    3: (self.bottomLeft, self.topRight),
                    4: (self.bottomRight,self.topLeft)}        
        item = switcher.get(n,(self.topRight, self.bottomLeft))  
        self.cornerVar = n 
        return item          
# ------------------------------------------------------
    def clear_maze(self):
        self.clear_widgets()
# ------------------------------------------------------
    def place_ball(self,cell,difficulty):
        x = cell.pos[0] + int(cell.size[0] / 2) - 6
        y = cell.pos[1] + int(cell.size[1] / 2) - 8
        width = int(cell.size[0] * .5) - 1
        height = int(cell.size[1] * .5) - 1
        speed = int((difficulty+2)/2)
        self.ball = Ball(size=(width,height),pos=(x,y),color=self.ballColor,speed=speed,size_hint=(None,None))
        self.add_widget(self.ball)
# ------------------------------------------------------
    def place_goal(self,cell): 
        if cell == self.bottomRight or cell == self.bottomLeft:
            x = cell.pos[0] + self.wallSize[0] - 1
            y = cell.pos[1] - int(self.floorSize[1]/2)
            src = self.assetData['goal_bottom']
        else:
            x = cell.pos[0] + self.wallSize[0] - 2
            y = cell.pos[1] + self.wallSize[1] - self.wallSize[0] - 3
            src = self.assetData['goal_top']
        w = self.floorSize[0]
        h = int(self.floorSize[1] * 2)
        Logger.debug(self.assetData)
        self.goal = Goal(pos=(x,y),size=(w,h), source=src, allow_stretch=True, keep_ratio = True)
        cell.add_widget(self.goal)
        self.goal.flash()
# ------------------------------------------------------
    def check_collisions(self,sprite,vector):
        newvector = vector
        x=vector[0]
        y=vector[1]
        for item in self.walls:
                try:
                    if item.obstacle:
                        newvector = sprite.check_collision(item,vector)
                        if newvector != vector:     #this code is supposed to allow us to check every sprite without overwriting vectors we already set to 0
                            if newvector[0] == 0:
                                x=0
                            if newvector[1] == 0:
                                y=0 
                except Exception:
                    Logger.Exception('{}: some kind of problem checking wall collisions'.format(self))
        for item in self.floors:
                try:
                    if item.obstacle:
                        newvector = sprite.check_collision(item,vector)
                        if newvector != vector:     
                            if newvector[0] == 0:
                                x=0
                            if newvector[1] == 0:
                                y=0 
                except Exception:
                    Logger.Exception('{}: some kind of problem checking floor collisions'.format(self))                   
        newvector = (x,y)
        return newvector 
# ------------------------------------------------------
    def check_victory(self,sprite,goal):
        item = sprite.collide_widget(goal)
        if item:
            (x,y) = goal.pos
            x = x + 6
            sprite.moveTo((x,y))
            goal.flash()
        return item                                    
# ------------------------------------------------------                      
    def move_sprite(self,player,sprite):
        v = player.get_vector()
        if v != (0,0):
            newvector = self.check_collisions(sprite,v)
            if newvector != (0,0) and newvector != None:
                sprite.move(newvector)
                player.SetVector(newvector)
# ------------------------------------------------------
    def choose_spriteset(self):
        pass
        

