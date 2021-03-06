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
        if active:
            self.activate()
        self.pos = (None,None)
        self.hasPrecedence = False
# ------------------------------------------------------    
    def get_vector(self):
        return self.vector  
# ------------------------------------------------------    
    def GetPos(self):
        return self.pos 
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
# ------------------------------------------------------  
    def activate(self):
        self.active = True
# ######################################################
class KeyboardHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            self.activate()
# ------------------------------------------------------  
    def activate(self):
        self.active = True
        self.rootWidget._keyboard = Window.request_keyboard(self._keyboard_closed, self.rootWidget, 'Keyboard Closed')
        self.rootWidget._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.rootWidget._keyboard.bind(on_key_up=self._on_keyboard_up)
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
        self.rootWidget._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.rootWidget._keyboard.unbind(on_key_up=self._on_keyboard_up)            
# ------------------------------------------------------    
    def _keyboard_closed(self):
        #print('My keyboard have been closed!')
        self.rootWidget._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.rootWidget._keyboard = None
# ------------------------------------------------------    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.hasPrecedence = True
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

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return False    
# ------------------------------------------------------   
    def _on_keyboard_up(self, keyboard, keycode):
        self.vector = (0,0)
        self.hasPrecedence = False

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
        if self.rootWidget.running and self.active:
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
                self.handle_touch_up(touch)
                touch.ungrab(self.rootWidget)
        return False                     
# ------------------------------------------------------    
    def SetVector(self,v):
        self.vector = v
        self.lastx = None
        self.lasty = None
# ------------------------------------------------------    
    def handle_touch_down(self, touch):
        self.hasPrecedence = True
        self.lastx = touch.x
        self.lasty = touch.y
        self.pos = (touch.x,touch.y)
        Logger.debug('{}.handle_touch_down: vector={}'.format(self,self.vector))
# ------------------------------------------------------    
    def handle_touch_up(self, touch):
        self.pos = (touch.x,touch.y)  
        self.lastx = None
        self.lasty = None
        self.hasPrecedence = True
# ------------------------------------------------------    
    def handle_touch_move(self, touch):
        self.pos = (touch.x,touch.y)
        self.vector = self.GetSwipeVector(touch)  
        self.lastx = touch.x
        self.lasty = touch.y    
        Logger.debug('{}.handle_touch_move: vector={}'.format(self,self.vector))          
# ------------------------------------------------------    
    def GetSwipeVector(self,touch,orientation='landscape'):
        vx = 0
        vy = 0
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
class TouchWidgetHandler(InputHandler):
        def __init__(self,rootWidget=None, active=True, parent=None,widget=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            self.activate(widget)
# ------------------------------------------------------  
    def SetWidget(self, widget):
        self.widget = widget

# ------------------------------------------------------  
    def activate(self, widget=None):
        if widget != None:
            self.SetWidget(widget)
        self.active = True
        if self.widget != None:
            self.widget.bind(on_touch_down=self._on_touch_down)
            self.widget.bind(on_touch_up=self._on_touch_up)
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
        if self.widget != None:
            self.widget.unbind(on_touch_down=self._on_touch_down)
            self.widget.unbind(on_touch_up=self._on_touch_up)                    
# ------------------------------------------------------    
    def _on_touch_down(self,instance,touch):
        if self.active and self.widget != None:
            touch.grab(self.widget)
            self.handle_touch_down(touch)
        return False  
# ------------------------------------------------------                
    def handle_touch_down(self, touch):
        target = self.widget.pos
        x = 0
        y = 0        
        if (touch.x > target.pos[0]):
            x = 1
        elif (touch.x < target.pos[0]):
            x = -1
        else:
            x = 0
        if (touch.y > target.pos[1]):
            y = 1
        elif (touch.y < target.pos[1]):
            yield = -1
        else:
            y = 0            
        self.vector = (x,y)
# ------------------------------------------------------
    def _on_touch_up(self,instance, touch):
        touch.ungrab(self.widget)
        return False     

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
            if b == lastb:
                x = 0
            elif b < lastb:
                x = -1 - bdiff
            elif b > lastb:
                x = 1 + bdiff
            if a == lasta:
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
# ######################################################
class HumInt():
    def __init__(self,rootWidget,useKeyboard=True,useTouchscreen=False,useAccelerometer=True,useJoystick=False,useTouchWidget=True,widget=None):
        self.keyboard = KeyboardHandler(active=useKeyboard, rootWidget=rootWidget, parent=self)
        self.touchscreen = TouchscreenHandler(active=useTouchscreen,rootWidget=rootWidget,parent=self)
        self.touchWidget = TouchWidgetHandler(active=useTouchWidget,widget=widget,parent=self)
        self.accControl = AccelerometerHandler(active=useAccelerometer,rootWidget=rootWidget,parent=self)
        #self.joystick = InputHandler(active=useJoystick)
        self.vector = (0,0)
        self.pos =  (0,0)
        self.lastVector = self.vector
# ------------------------------------------------------    
    def get_vector(self):
        v = (0,0)
        if self.keyboard.active and self.keyboard.hasPrecedence:
            v = self.keyboard.get_vector()
        elif self.touchscreen.active and self.touchscreen.hasPrecedence:
            v = self.touchscreen.get_vector()
        elif self.accControl.active:
            v = self.accControl.get_vector()
        self.vector = v
        return v
# ------------------------------------------------------    
    def SetVector(self,v):
        self.vector = v
        if (self.touchscreen.active):
            self.touchscreen.SetVector(v)   
# ------------------------------------------------------
    def SetWidget(self,widget):
        self.touchWidget.SetWidget(widget)
