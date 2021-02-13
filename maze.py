#system imports
import numpy as np

#kivy imports
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import (NumericProperty, BoundedNumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock

#local imports
from ellermaze import EllerMaze
from ellermaze import EllerMazeGenerator
import humint as hi
from mazesprites import (Cell, Wall, Floor, Ball, Goal)
from menu import GameMenu


class MazeApp(App):
    def build(self):
        super().__init__()
        #print('MazeApp.build')
        game = MazeGame()
        game.start()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

# Cool colors:
#   175/256,176/256,148/256,1
#   .084, .098, .120, .9


class MazeGame(Widget):
    mazeGenerator = ObjectProperty(None)
    gridHeight = ObjectProperty(None)
    gridWidth = ObjectProperty(None)
    player1 = ObjectProperty(None)
    difficulty = BoundedNumericProperty(3, min=1, max=5)
    running = False
    playfield = ObjectProperty(None)

    def start(self):
        #print('MazeGame.start')
        self.playfield = Playfield()
        self.add_widget(self.playfield)
        self.playfield.size = (640,640)
        self.size = self.playfield.size
        bottom = 0
        left = 0 + 8
        self.playfield.pos = (left, bottom)
        self.difficulty = 3
        self.end_game(victory=False)
        #self.new_game(difficulty=self.difficulty)

    def new_game(self,difficulty):
        dm = self.get_grid_size(difficulty)
        mg = EllerMazeGenerator(dm[0], dm[1])
        self.playfield.hide_menu()
        self.playfield.DrawMaze(mg.GetMaze())
        self.playfield.PlaceGoal(self.playfield.end)
        self.playfield.PlaceBall(self.playfield.start)
        self.player1 = hi.HumInt()
        self.running = True

    def get_grid_size(self,difficulty):
        switcher = {
            1: (10,10),
            2: (12,12),
            3: (14,14),
            4: (16,16),
            5: (18,18)
            }
        item = switcher.get(difficulty,(12,12))
        return item
# ------------------------------------------------------
    def update(self, dt):
        if (self.running):
            self.running_update()
        else:
            self.paused_update()
# ------------------------------------------------------
    def running_update(self):
        self.playfield.MoveSprite(self.player1,self.playfield.ball)   
        victory = self.playfield.CheckVictory(self.playfield.ball,self.playfield.goal)  
        if victory:
            self.end_game(victory)
# ------------------------------------------------------
    def paused_update(self):
        m = self.playfield.gameMenu
        m.update()
        if m.newFlag:
            self.difficulty = m.difficulty
            self.new_game(self.difficulty) 
        elif m.quitFlag:
            self.quit()    
 # ------------------------------------------------------               
    def end_game(self, victory=True):
        print('end_game')
        self.running = False
        self.playfield.show_menu(self.difficulty)
# ------------------------------------------------------
    def quit(self):
        self.playfield.hide_menu()
        print('Goodbye!')
        exit()
# ------------------------------------------------------
    #bind touch events to controller object
    def on_touch_down(self, touch):
        print('MazeGame.on_touch_down')
        if self.running:
            touch.grab(self)
            if (self.player1 != None):
                self.player1.Handle_Touch_Down(touch)
        return super().on_touch_down(touch)                
# ------------------------------------------------------    
    def on_touch_move(self, touch):
        if self.running:
            if touch.grab_current is self:
                # now we only handle moves which we have grabbed
                if (self.player1 != None):
                    self.player1.Handle_Touch_Move(touch)
        return super().on_touch_move(touch)                    
# ------------------------------------------------------
    def on_touch_up(self, touch):
        print('MazeGame.on_touch_up')
        if self.running:
            if touch.grab_current is self:
                touch.ungrab(self)
                if (self.player1 != None):
                    self.player1.Handle_Touch_Up(touch)
        return super().on_touch_up(touch)                    

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
    def show_menu(self,difficulty):
        self.gameMenu = GameMenu(difficulty=difficulty)
        self.add_widget(self.gameMenu)
# ------------------------------------------------------
    def hide_menu(self):
        self.remove_widget(self.gameMenu)           
 # ------------------------------------------------------   
    def DrawMaze(self,maze):
        #print('Playfield.DrawMaze')
        self.clear_widgets()
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

        # for child in self.children:
            # #print(child.x,',',child.y,',',child.canvas)
        self.bottomRight = self.children[0]
        self.bottomLeft = self.children[w-1]
        self.topLeft = self.children[(w-1)*h-1]
        self.topRight = self.children[(w-2)*h+1]
        self.start = self.topRight
        self.end = self.bottomLeft
        
# ------------------------------------------------------
    def ClearMaze():
        self.clear_widgets()
# ------------------------------------------------------
    def PlaceBall(self,cell):
        x = cell.pos[0] + int(cell.size[0] / 2) - 6
        y = cell.pos[1] + int(cell.size[1] / 2) - 8
        width = int(cell.size[0] * .5)
        height = int(cell.size[1] * .5)
        #print(self.ballColor)
        self.ball = Ball(size=(width,height),pos=(x,y),color=self.ballColor,size_hint=(None,None))
        self.add_widget(self.ball)
# ------------------------------------------------------
    def PlaceGoal(self,cell):
        w = int(cell.size[0])
        h = int(cell.size[1])        
        x = cell.pos[0] - int(w / 2 )
        y = cell.pos[1] - int(h / 2) #- 8
        #print(cell.pos,cell.size)
        self.goal = Goal(pos=(x,y),size=(w,h),textColordata=self.goalColordata)
        self.add_widget(self.goal)
        self.goal.moveTo(cell.pos)       
# ------------------------------------------------------
    def CheckCollissions(self,sprite,vector):
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
    def CheckVictory(self,sprite,goal):
        item = sprite.collide_widget(goal)
        return item                                    
  # ------------------------------------------------------                      

    def MoveSprite(self,player,sprite):
        v = player.GetVector()
        if v != (0,0):
            newvector = self.CheckCollissions(sprite,v)
            if newvector != (0,0):
                sprite.move(newvector)

        

