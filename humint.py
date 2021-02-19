from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
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
        self.rootWidget._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'Keyboard Closed')
        self.rootWidget._keyboard.bind(on_key_down=self._on_keyboard_down)
# ------------------------------------------------------    
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self.rootWidget._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.rootWidget._keyboard = None
# ------------------------------------------------------    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print (keycode)
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
        self.rootWidget.bind(on_touch_down=self._on_touch_down)
        self.rootWidget.bind(on_touch_move=self._on_touch_move)
        self.rootWidget.bind(on_touch_up=self._on_touch_up)
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
        self.lastx = None
        self.lasty = None
# ------------------------------------------------------    
    def handle_touch_move(self, touch):
        self.pos = (touch.x,touch.y)
        self.vector = self.GetSwipeVector(touch)  
        #print('self.vector=',self.vector)
        self.lastx = touch.x
        self.lasty = touch.y     
        self.update_parent()         
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

# #######################################################
class AccelerometerHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        self.active = False
        try:
            self.rootWidget.accelerometer.enable()
            self.accelerometer = self.rootWidget.accelerometer
            #self.accelerometer.enable()
            self.init_value()
            self.active = True
        except AttributeError:
            import traceback
            traceback.print_exc()
            status = "Accelerometer is not implemented for your platform"
            print(status)
# ------------------------------------------------------  
    def init_value(self):
        self.value = self.accelerometer.acceleration[:3]
        self.lastvalue = self.value
# ------------------------------------------------------  
    def get_vector(self):
        if self.active:
            self.value = self.accelerometer.acceleration[:3]
            if not self.value == (None, None, None):
                if self.value[0] < self.lastvalue[0]:
                    x = -1
                elif self.value[0] > self.lastvalue[0]:
                    x = 1
                else:
                    x = 0
                if self.value[1] < self.lastvalue[1]:
                    y = -1
                elif self.value[1] > self.lastvalue[1]:
                    y = 1
                else:
                    y = 0
                self.vector = (x,y)
        return self.vector

# ######################################################
class HumInt():
    # lastVector = ObjectProperty(None)
    # keyboard = ObjectProperty(None)
    # touchscreen = ObjectProperty(None)
    # mouse  = ObjectProperty(None)
    # joystick = ObjectProperty(None)

    def __init__(self,rootWidget,useKeyboard=True,useTouchscreen=True,useAccelerometer=True,useJoystick=False):
        self.keyboard = KeyboardHandler(active=useKeyboard, rootWidget=rootWidget, parent=self)
        self.touchscreen = TouchscreenHandler(active=useTouchscreen,rootWidget=rootWidget,parent=self)
        self.accelerometer = AccelerometerHandler(active=useAccelerometer,rootWidget=rootWidget,parent=self)
        #self.joystick = InputHandler(active=useJoystick)
        self.vector = (0,0)
        self.pos =  (0,0)
        self.lastVector = self.vector
# ------------------------------------------------------    
    def get_vector(self):
        v = self.vector
        return v
# ------------------------------------------------------    
    def SetVector(self,v):
        self.vector = v
        if (self.touchscreen.active):
            self.touchscreen.SetVector(v)   

