from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.logger import Logger
from plyer import accelerometer

class InputHandler():

    def __init__(self,rootWidget=None, active=True, parent=None):
        self.rootWidget = rootWidget
        self.parent = parent
        self.lastx = None
        self.lasty = None
        self.vector = (0,0)
        self.active = active
        self.pos = (None,None)
# ------------------------------------------------------    
    def get_vector(self):
        return self.vector  
# ------------------------------------------------------    
    def GetPos(self):
        return self.pos 
# ------------------------------------------------------    
    def update_parent(self):
        if self.parent != None:
            try:
                self.parent.vector = self.vector
                #print(self.parent,self.parent.vector)
            except Exception:
                pass

# ######################################################
class KeyboardHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            self.activate()
# ------------------------------------------------------  
    def activate(self):
        self.active = True
        self.rootWidget._keyboard = Window.request_keyboard(self._keyboard_closed, rootWidget, 'Keyboard Closed')
        self.rootWidget._keyboard.bind(on_key_down=self._on_keyboard_down)
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
        self.rootWidget._keyboard.unbind(on_key_down=self._on_keyboard_down)            
# ------------------------------------------------------    
    def _keyboard_closed(self):
        #print('My keyboard have been closed!')
        self.rootWidget._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.rootWidget._keyboard = None
# ------------------------------------------------------    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print (keycode)
        x = self.vector[0]
        y = self.vector[1]
        t = keycode[1]
        if t == 'left':
            x = -1
        elif t == 'right':
            x = 1
        if t == 'up':
            y = 1
        elif t == 'down':
            y = -1
        self.vector = (x,y)
        self.update_parent()

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return False    

# #######################################################
class TouchscreenHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            self.activate()
# ------------------------------------------------------  
    def activate(self):
        self.active = True
        self.rootWidget.bind(on_touch_down=self._on_touch_down)
        self.rootWidget.bind(on_touch_move=self._on_touch_move)
        self.rootWidget.bind(on_touch_up=self._on_touch_up)
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
        self.rootWidget.unbind(on_touch_down=self._on_touch_down)
        self.rootWidget.unbind(on_touch_move=self._on_touch_move)
        self.rootWidget.unbind(on_touch_up=self._on_touch_up)                    
# ------------------------------------------------------    
    def _on_touch_down(self,instance,touch):
        if self.rootWidget.running:
            touch.grab(self.rootWidget)
            self.handle_touch_down(touch)
        return False
# ------------------------------------------------------    
    def _on_touch_move(self,instance,touch):
        if self.rootWidget.running:
            if touch.grab_current is self.rootWidget:
                # now we only handle moves which we have grabbed
                self.handle_touch_move(touch)
        return False                    
# ------------------------------------------------------
    def _on_touch_up(self,instance, touch):
        if self.rootWidget.running:
            if touch.grab_current is self.rootWidget:
                touch.ungrab(self.rootWidget)
                self.handle_touch_up(touch)
        return False                     
# ------------------------------------------------------    
    def SetVector(self,v):
        self.vector = v
        self.lastx = None
        self.lasty = None
# ------------------------------------------------------    
    def handle_touch_down(self, touch):
        self.lastx = touch.x
        self.lasty = touch.y
        self.pos = (touch.x,touch.y)
# ------------------------------------------------------    
    def handle_touch_up(self, touch):
        self.pos = (touch.x,touch.y)
        self.vector = self.GetSwipeVector(touch)
        self.update_parent()  
        self.lastx = None
        self.lasty = None
# ------------------------------------------------------    
    def handle_touch_move(self, touch):
        self.pos = (touch.x,touch.y)
        # self.vector = self.GetSwipeVector(touch)  
        # #print('self.vector=',self.vector)
        # self.lastx = touch.x
        # self.lasty = touch.y     
        # self.update_parent()         
# ------------------------------------------------------    
    def GetSwipeVector(self,touch):
        vx = 0
        vy = 0
        #print('before getting swipe vector')
        if (self.lastx != None) and (self.lasty != None):
            #print('getting swipe vector')
            x = touch.x
            y = touch.y
            if (x < self.lastx):
                vy = 1
            elif (x > self.lastx):
                vy = -1
            else:
                vy = 0
            if (y < self.lasty):
                vx = -1
            elif (y > self.lasty):
                vx = 1
            else:
                vx=0
        v = (vx,vy)                
        return v

# #######################################################
class AccelerometerHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            try:
                self.active = True
                accelerometer.enable()
            except NotImplementedError:
                import traceback
                traceback.print_exc()
                status = "{}: Accelerometer is not implemented for your platform".format(self)
                Logger.info(status)
                #print(status)
                self.active = False
            if self.active:
                self.init_value()
# ------------------------------------------------------  
    def init_value(self):
        self.value = accelerometer.acceleration[:3]
        self.lastvalue = self.value
# ------------------------------------------------------  
    def get_vector(self):
        if self.active:
            a = 0
            b = 0
            lasta = a
            lastb = b
            self.value = accelerometer.acceleration[:3]
            if self.value != (None, None, None):
                a = round(self.value[0],1)
                b = round(self.value[1],1)
            if self.lastvalue != (None, None, None):
                lasta = round(self.lastvalue[0],1)
                lastb = round(self.lastvalue[1],1)
            adiff = int(abs(a-lasta))
            if adiff > 6:
                adiff = 6
            bdiff = int(abs(b-lastb))
            if bdiff > 6:
                bdiff = 6
            if b == lastb or b == 0:
                x = 0
            elif b < lastb:
                x = -1 - bdiff
            elif b > lastb:
                x = 1 + bdiff
            if a == lasta or a == 0:
                y = 0
            if a < lasta:
                y = 1 + adiff 
            elif a > lasta:
                y = -1 - adiff 
            self.vector = (x,y)
        return self.vector
# ------------------------------------------------------  
    def update(self):
        if self.active:
            self.vector = self.get_vector()
            self.update_parent()
# ######################################################
class HumInt():
    def __init__(self,rootWidget,useKeyboard=False,useTouchscreen=True,useAccelerometer=True,useJoystick=False):
        self.keyboard = KeyboardHandler(active=useKeyboard, rootWidget=rootWidget, parent=self)
        self.touchscreen = TouchscreenHandler(active=useTouchscreen,rootWidget=rootWidget,parent=self)
        self.accControl = AccelerometerHandler(active=useAccelerometer,rootWidget=rootWidget,parent=self)
        #self.joystick = InputHandler(active=useJoystick)
        self.vector = (0,0)
        self.pos =  (0,0)
        self.lastVector = self.vector
# ------------------------------------------------------    
    def get_vector(self):
        self.accControl.update()
        v = self.vector
        return v
# ------------------------------------------------------    
    def SetVector(self,v):
        self.vector = v
        if (self.touchscreen.active):
            self.touchscreen.SetVector(v)   

