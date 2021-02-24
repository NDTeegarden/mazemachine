# from https://github.com/BSolonenko/Maze-Generator
import random
import numpy as np
from kivy.logger import Logger

class EllerMaze(object):

    def __init__(self, w, h):
        self.Width = w
        self.Height = h 
        self.m_EllerMaze = {}

    def SetWay(self, f, t):
        self.SetOrderedWay(f, t)
        self.SetOrderedWay(t, f)
    
    def SetOrderedWay(self, f, t):
        f = str(f)
        if(not f in self.m_EllerMaze):
            self.m_EllerMaze[f] = []
        self.m_EllerMaze[f].append(t)

    def HasPath(self, f, t):
        f = str(f)
        if(not f in self.m_EllerMaze):
            return False
        return t in self.m_EllerMaze[f]

    def GetVertex(self, x, y):
        return self.Width * y + x

    def Print(self):
        str = ''
        for x in range(self.Width):
            str += ' __'
        print(str)
        for y in range(self.Height):
            str = ''
            for x in range(self.Width):
                if(x != 0 and self.HasPath(self.GetVertex(x, y), self.GetVertex(x - 1, y))):
                    str += ' '
                else:
                    str += '|'
                if(self.HasPath(self.GetVertex(x, y), self.GetVertex(x, y + 1))):
                    str += '  '
                else:
                    str += '__'
            print(str + '|')
        print('') 

    def ToArray(self):
        w = self.Width 
        h = self.Height 
        grid = np.zeros([w,h,2])  #3D matrix: height by width by [(wall true or false),(floor true or false)]
        for y in range(h):
            for x in range(w):
                if(x != 0 and self.HasPath(self.GetVertex(x, y), self.GetVertex(x - 1, y))):
                    grid[x,y,0] = False      #No wall
                else:
                    grid[x,y,0]  = True    #Wall
                if(self.HasPath(self.GetVertex(x, y), self.GetVertex(x, y + 1))):
                    grid[x,y,1]  = False   #No Floor
                else:
                    grid[x,y,1] = True     #Floor

        #Now create a new grid one column and row larger than the original
        newgrid = np.zeros([w+1,h+1,2]) 
        #add the ceiling
        y = 0
        for x in range(w):
            newgrid[x,y,0] = False     #No wall
            newgrid[x,y,1] = True      #Floor
        newgrid[w,y,0] = False
        newgrid[w,y,1] = False
        #copy over the old grid, adding a wall to the end of each row
        for y in range(1,h+1):
            for x in range(w):
                newgrid[x,y,0] = grid[x, y-1, 0]
                newgrid[x,y,1] = grid[x, y-1, 1]
            newgrid[w,y,0] = True
            newgrid[w,y,1] = False

        return newgrid     
      

# #####################################
class EllerMazeGenerator(object):
    def __init__(self, w, h):
        self.Width = max(1, w)
        self.Height = max(1, h)
        self.Generate()

    def InitSet(self):
        self.m_LastSetNumber = 0 
        self.m_Set = []
        for i in range(self.Width):
            self.m_LastSetNumber += 1
            self.m_Set.append(self.m_LastSetNumber)

    def DestroyLeftWalls(self, y):
        for x in range(1, self.Width):
            if(self.m_Set[x] != self.m_Set[x - 1] and random.choice([True, False])):
                self.SetWay(x - 1, y, x, y)

    def DestroyDownLines(self, y):
        hasDownWay = False
        for x in range(self.Width):
            if(random.choice([True, False])):
                self.SetWay(x, y, x, y + 1)
                hasDownWay = True
            if(x == self.Width - 1 or self.m_Set[x] != self.m_Set[x + 1]):
                if(hasDownWay):
                    hasDownWay = False
                else:
                    self.SetWay(x, y, x, y + 1)

    def UpdateSet(self, y):
        for x in range(self.Width):
            if(not self.HasPath(x, y, x, y + 1)):
                self.m_LastSetNumber += 1
                self.m_Set[x] = self.m_LastSetNumber

    def ProcessLastLine(self):
        y = self.Height - 1
        for x in range(1, self.Width):
            if(self.m_Set[x] != self.m_Set[x-1]):
                self.SetWay(x, y, x - 1, y)

    def Generate(self):
        self.m_Maze = EllerMaze(self.Width, self.Height)  
        self.InitSet()
        for y in range(self.Height - 1):   
            self.DestroyLeftWalls(y)
            self.DestroyDownLines(y)
            self.UpdateSet(y)
        self.ProcessLastLine()
        return self.m_Maze

    def MergeSet(self, x1, x2):
        setNumToReplace = max(self.m_Set[x1], self.m_Set[x2])
        newSetNum = min(self.m_Set[x1], self.m_Set[x2])
        for x in range(self.Width):
            if(self.m_Set[x] == setNumToReplace):
                self.m_Set[x] = newSetNum

    def SetWay(self, x1, y1, x2, y2):
        self.m_Maze.SetWay(self.m_Maze.GetVertex(x1, y1), self.m_Maze.GetVertex(x2, y2))
        self.MergeSet(x1, x2)

    def HasPath(self, x1, y1, x2, y2):
        return self.m_Maze.HasPath(self.m_Maze.GetVertex(x1, y1), self.m_Maze.GetVertex(x2, y2))

    def GetMaze(self):
        return self.m_Maze
