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

#system imports
import sys
import numpy as np
import random as rn


class MazeApp(App):
    def build(self):
        super().__init__()
        #print('MazeApp.build')
        game = MazeGame()
        game.start()
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
    def start(self):
        #print('MazeGame.start')
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
        dm = self.get_grid_size(self.difficulty)
        mg = EllerMazeGenerator(dm[0], dm[1])
        self.playfield.draw_maze(mg.GetMaze())
        self.playfield.place_goal(self.playfield.end)
        self.playfield.place_ball(cell=self.playfield.start,difficulty=self.difficulty)
        self.player1 = HumInt(rootWidget=self)
        self.running = True
        self.loopEvent = Clock.schedule_interval(self.update, 1.0 / 60.0)
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
    x_offset = 0
    y_offset = 0
    topLeft = ObjectProperty(None)
    bottomLeft = ObjectProperty(None)
    topRight = ObjectProperty(None)
    bottomRight = ObjectProperty(None)
    ball = ObjectProperty(None)
    start = ObjectProperty(None)
    end = ObjectProperty(None)
    gameMenu = ObjectProperty(None)

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
        with self.canvas:
            self.color = backColor
            self.rect = Rectangle(pos=self.pos,size=self.size)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
# ------------------------------------------------------
    def update_canvas(self,*args): 
        #print('Playfield.update_canvas') 
        self.update_rect()    
# ------------------------------------------------------
    def update_rect(self):
        self.rect.pos = self.pos
        self.rect.size = self.size         
 # ------------------------------------------------------   
    def draw_maze(self,maze):
        self.clear_maze()
        mtrx = maze.ToArray()
        
        w = mtrx.shape[0]  #number of cells wide
        h = mtrx.shape[1] #number of cells high
        cw = int(self.width / (w + 1))
        ch = int(self.height / (h + 1))
        for y in range (h):
            for x in range (w):
                ##print(x,',',y)
                #add a blank cell to the layout
                invy = h-y    #because kivy puts 0,0 on bottom left
                #print('About to create a cell...')
                c = Cell(pos=((x*cw)+self.xoffset,(invy*ch)-self.yoffset), size=(cw,ch),color=self.cellColor)
                #print('done')
                self.add_widget(c)
                #look up the grid position and see if we need to add a wall and/or floor to the cell
                if (mtrx[x,y,0]):
                    c.add_widget(Wall(pos=c.pos,size=(int(cw/5),int(ch + ch/5)),color=self.wallColor)) 
                if (mtrx[x,y,1]):
                    c.add_widget(Floor(pos=c.pos,size=(cw,int(ch/5)),color=self.wallColor))
        self.bottomRight = self.children[1]
        self.bottomLeft = self.children[w-1]
        self.topLeft = self.children[(w-1)*h-1]
        self.topRight = self.children[(w-2)*h+1]   
        self.select_corners()
# ------------------------------------------------------
    def select_corners(self):     
        n = rn.randint(1,4)
        Logger.debug('{}:n={}'.format(self,n))
        if n == 1:
            self.start = self.topRight
            self.end = self.bottomLeft
        elif n == 2:
            self.start = self.topLeft
            self.end = self.bottomRight
        elif n == 3:
            self.start = self.bottomLeft
            self.end = self.topRight
        else:
            self.start = self.bottomRight
            self.end = self.topLeft                  
# ------------------------------------------------------
    def clear_maze(self):
        self.clear_widgets()
# ------------------------------------------------------
    def place_ball(self,cell,difficulty):
        x = cell.pos[0] + int(cell.size[0] / 2) - 6
        y = cell.pos[1] + int(cell.size[1] / 2) - 8
        width = int(cell.size[0] * .5)
        height = int(cell.size[1] * .5)
        #print(self.ballColor)
        self.ball = Ball(size=(width,height),pos=(x,y),color=self.ballColor,speed=int((difficulty+1)/2),size_hint=(None,None))
        self.add_widget(self.ball)
# ------------------------------------------------------
    def place_goal(self,cell):
        w = int(cell.size[0])
        h = int(cell.size[1])        
        x = cell.pos[0] #- int(w / 2 )
        y = cell.pos[1] #- int(h / 2) #- 8
        #print(cell.pos,cell.size)
        self.goal = Goal(pos=(x+int(w * .22),y+int(h * .22)),size=(int(w * .8),int(h * .8)), source='assets/exit.png')
        cell.add_widget(self.goal)
        #self.goal.moveTo(cell.pos)       
# ------------------------------------------------------
    def check_collisions(self,sprite,vector):
        newvector = vector
        h=vector[0]
        v=vector[1]
        for c in self.children:     # all the cells
            if c != sprite:
                for g in c.children:    #each wall and floor within the cell
                    try:
                        if g.obstacle:
                            newvector = sprite.check_collision(g,vector)
                            if newvector != vector:     #this code is supposed to allow us to check every sprite without overwriting vectors we already set to 0
                                if newvector[0] == 0:
                                    #print('setting h to 0')
                                    h=0
                                if newvector[1] == 0:
                                    #print('setting v to 0')
                                    v=0 
                    except Exception:
                        pass
        newvector = (h,v)
        #print(newvector)
        return newvector 
# ------------------------------------------------------
    def check_victory(self,sprite,goal):
        item = sprite.collide_widget(goal)
        return item                                    
# ------------------------------------------------------                      
    def move_sprite(self,player,sprite):
        v = player.get_vector()
        if v != (0,0):
            newvector = self.check_collisions(sprite,v)
            if newvector != (0,0) and newvector != None:
                sprite.move(newvector)
                player.SetVector(newvector)

        

