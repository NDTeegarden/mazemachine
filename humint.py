import keyboard as kb
#import mouse as m
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)

class InputHandler():

    def __init__(self,active = True):
        self.lastx = None
        self.lasty = None
        self.vector = (None,None)
        self.active = active
        self.pos = (None,None)

    def GetVector(self):
        return self.vector  

    def GetPos(self):
        return self.pos                

class KeyboardHandler(InputHandler):
    pass


class MouseHandler(InputHandler):
    def Handle_Mouse_Move(self,mouse):
        pass

class TouchscreenHandler(InputHandler):
    def SetVector(self,v):
        self.vector = v
        self.lastx = None
        self.lasty = None

    def Handle_Touch_Down(self, touch):
        self.lastx = touch.x
        self.lasty = touch.y
        self.pos = (touch.x,touch.y)

    def Handle_Touch_Up(self, touch):
        self.pos = (touch.x,touch.y)
        self.lastx = None
        self.lasty = None

    def Handle_Touch_Move(self, touch):
        self.pos = (touch.x,touch.y)
        self.vector = self.GetSwipeVector(touch)  
        #print('self.vector=',self.vector)
        self.lastx = touch.x
        self.lasty = touch.y              

    def GetSwipeVector(self,touch):
        vx = 0
        vy = 0
        #print('before getting swipe vector')
        if (self.lastx != None) and (self.lasty != None):
            #print('getting swipe vector')
            x = touch.x
            y = touch.y
            if (x < self.lastx):
                vx = -1
            elif (x > self.lastx):
                vx = 1
            else:
                vx = 0
            if (y < self.lasty):
                vy = -1
            elif (y > self.lasty):
                vy = 1
            else:
                vy=0
        v = (vx,vy)                
        return v


class HumInt():
    # lastVector = ObjectProperty(None)
    # keyboard = ObjectProperty(None)
    # touchscreen = ObjectProperty(None)
    # mouse  = ObjectProperty(None)
    # joystick = ObjectProperty(None)

    def __init__(self,useKeyboard=True,useTouchscreen=True,useMouse=True,useJoystick=False):
        #self.keyboard = KeyboardHandler(active=useKeyboard)
        self.touchscreen = TouchscreenHandler(active=useTouchscreen)
        #self.mouse = InputHandler(active=useMouse)
        #self.joystick = InputHandler(active=useJoystick)
        self.vector = (0,0)
        self.pos =  (0,0)
        self.lastVector = self.vector

    def GetVector(self):
        v = self.vector
        return v

    def SetVector(self,v):
        self.vector = v
        if (self.touchscreen.active):
            self.touchscreen.SetVector(v)   

    def Handle_Touch_Down(self,touch):
        self.touchscreen.Handle_Touch_Down(touch)
        #print("touch_down")
        self.vector = (0,0)

    def Handle_Touch_Move(self,touch):
        #print("touch_move")
        self.touchscreen.Handle_Touch_Move(touch)
        self.vector = self.touchscreen.GetVector()  
        #print(self.vector)  

    def Handle_Touch_Up(self,touch):
        #print("touch_up")
        self.touchscreen.Handle_Touch_Up(touch)
        self.vector = self.touchscreen.GetVector()
        #print(self.vector)              

