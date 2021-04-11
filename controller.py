from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.logger import Logger, LOG_LEVELS
from plyer import accelerometer
import threading as th

class InputHandler():

    def __init__(self,rootWidget=None, active=True, parent=None):
        self.rootWidget = rootWidget
        self.parent = parent
        self.lastx = None
        self.lasty = None
        self.vector = (0,0)
        if active:
            self.activate()
        else:
            self.active = False
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
        if self.parent.enabled and self.active:
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
class TouchWidgetHandler(InputHandler):
    def __init__(self,rootWidget=None, active=True, parent=None,widget=None):
        super().__init__(rootWidget=rootWidget, active=active, parent=parent)
        if active:
            self.activate(widget)
# ------------------------------------------------------  
    def set_widget(self, widget):
        self.widget = widget
# ------------------------------------------------------  
    def activate(self, widget=None):
        if widget != None:
            self.set_widget(widget)
        self.active = True
        if self.widget != None:
            self.widget.bind(on_touch_down=self._on_touch_down)
            self.widget.bind(on_touch_move=self._on_touch_move)
            self.widget.bind(on_touch_up=self._on_touch_up)
# ------------------------------------------------------  
    def deactivate(self):
        self.active = False
        if self.widget != None:
            self.widget.unbind(on_touch_down=self._on_touch_down)
            self.widget.unbind(on_touch_move=self._on_touch_move)
            self.widget.unbind(on_touch_up=self._on_touch_up)                    
# ------------------------------------------------------    
    def _on_touch_down(self,instance,touch):
        thread = th.Thread(target=self.handle_touch_down, args=(touch.pos,))
        thread.start()
        return False 
# ------------------------------------------------------    
    def _on_touch_move(self,instance,touch):
        thread = th.Thread(target=self.handle_touch_down, args=(touch.pos,))
        thread.start()
        return False           
# ------------------------------------------------------                
    def handle_touch_down(self, pos):
        if self.parent.enabled and self.active and self.widget != None:        
            self.hasPrecedence = True
            self.pos = pos
# ------------------------------------------------------
    def _on_touch_up(self,instance, touch):
        self.hasPrecedence = False 
        return False    
# ------------------------------------------------------
    def handle_touch_up(self):
        pass
# ------------------------------------------------------    
    def get_vector(self):
        targetPos = self.widget.pos
        touchPos = self.pos
        xdiff = touchPos[0] - targetPos[0]
        ydiff = touchPos[1] - targetPos[1]
        if (abs(xdiff)-self.widget.size[0]/2) > abs(ydiff):
            ydiff = 0
        elif (abs(ydiff)-self.widget.size[1]/2) > abs(xdiff):
            xdiff = 0
        x = 0
        y = 0        
        if (xdiff > 0):
            x = 1
        elif (xdiff < 0):
            x = -1
        else:
            x = 0
        if (ydiff > 0 ):
            y = 1
        elif (ydiff < 0):
            y = -1
        else:
            y = 0            
        self.vector = (x,y)        
        return self.vector             
# ######################################################
class JoystickHandler(InputHandler):
# ------------------------------------------------------  
    def activate(self):
        self.active = True
        Window.bind(on_joy_axis=self._on_joy_axis)
        Window.bind(on_joy_hat=self._on_joy_hat)
        Window.bind(on_joy_button_down=self._on_joy_button_down)
        Window.bind(on_joy_up_down=self._on_joy_button_up)
# ------------------------------------------------------
    def _on_joy_hat(self, win, arg1, arg2, value):
        thread = th.Thread(target=self.handle_hat, args=(arg1, arg2, value))
        thread.start()
        return False
# ------------------------------------------------------  
    def handle_hat(self, arg1, arg2, value):
        if self.parent.enabled and self.active:
            vector = value
            self.vector = vector  
            self.hasPrecedence = True        
# ------------------------------------------------------  
    def _on_joy_button_down(self, win, arg1, number):
        thread = th.Thread(target=self.handle_button_down, args=(arg1, number))
        thread.start()
        return False
# ------------------------------------------------------  
    def handle_button_down(self, arg1, number):
        if self.parent.enabled and self.active:
            if number==11:
                self.vector = (0,1)
            elif number==12:
                self.vector = (0,-1)
            elif number==13:
                self.vector = (-1,0)    
            elif number==14:
                self.vector = (1,0)
            else:
                Logger.debug('Joystick {} button {} pressed.'.format(arg1, number))   
# ------------------------------------------------------  
    def handle_button_up(self, arg1, number):
        if self.parent.enabled and self.active:
            if number >= 11 and number <= 14:
                self.vector = (0,0)
            else:
                Logger.debug('Joystick {} button {} released.'.format(arg1, number))                       
# ------------------------------------------------------  
    def _on_joy_button_up(self, win, arg1, number):
        self.hasPrecedence = False
        thread = th.Thread(target=self.handle_button_up, args=(arg1, number) )
        thread.start()
        return False 
# ------------------------------------------------------  
    def _on_joy_axis(self, win, stickid, axisid, value):
        #self.hasPrecedence = True
        #thread = th.Thread(target=self.handle_stick, args=(stickid, axisid, value))
        #thread.start()
        return False
# ------------------------------------------------------  
    def handle_stick(self, stickid, axisid, value):   
        Logger.debug('{}: stick={}  axis={}  value={}'.format(self, stickid, axisid, value)) 
        threshhold = 2048
        if abs(value) <= threshhold:
            value = 0
        x = 0
        y = 0
        if value < 0:
            d = -1
        elif value > 0:
            d = 1
        else:
            d = 0
        if axisid==1 or axisid==4:
            y = d
        elif axisid==0 or axisid==3:
            x = d
        self.vector = (x,y)

# ------------------------------------------------------ 
    def deactivate(self):
        self.active = False
        self.hasPrecedence = False
        Window.unbind(on_joy_axis=self._on_joy_axis)
        Window.unbind(on_joy_hat=self._on_joy_hat)
        Window.unbind(on_joy_button_down=self._on_joy_button_down)
        Window.unbind(on_joy_up_down=self._on_joy_button_up)        
# ------------------------------------------------------    
    def get_vector(self):
        v = self.vector
        if v == (0,0):
            self.hasPrecedence = False
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
                status = '{}: Accelerometer is not implemented for your platform'.format(self)
                Logger.info(status)
                self.active = False
            if self.active:
                self.init_value()
# ------------------------------------------------------  
    def init_value(self):
        self.value = accelerometer.acceleration[:3]
        self.lastvalue = self.value
        status = '{}init_value: value={}   lastvalue={}'.format(self, self.value, self.lastvalue)
        Logger.debug(status)     
# ------------------------------------------------------  
    def get_vector(self):
        if self.parent.enabled and self.active:
            maxdiff = 2
            mindiff = 1
            threshold = .125
            self.value = accelerometer.acceleration[:3]
            #status = '{}get_vector: value={}   lastvalue={}'.format(self, self.value, self.lastvalue)
            #Logger.debug(status)
            if self.value != (None, None, None):
                a = round(self.value[0]-self.value[2],1)   
                b = round(self.value[1]-self.value[2],1)
            else:
                a = 0
                b = 0
            if self.lastvalue != (None, None, None):
                lasta = round(self.lastvalue[0]-self.lastvalue[2],1)   
                lastb = round(self.lastvalue[1]-self.value[2],1)
            else:
                lasta = a
                lastb = b           
#           Get the difference between this reading with the last reading       
            xdiff = abs(b-lastb)
            if xdiff <= threshold:
                xdiff = 0
            elif xdiff < mindiff:
                xdiff = mindiff
            elif xdiff > maxdiff:
                xdiff = maxdiff
            ydiff = abs(a-lasta)
            if ydiff <= threshold:
                ydiff = 0
            elif ydiff < mindiff:
                ydiff = mindiff
            elif ydiff > maxdiff:
                ydiff = maxdiff
#           Get vector values between -1 and 1
            if xdiff == 0:
                x = 0   #this should catch moves below the threshold so the ball isn't constantly jiggling
            elif b < lastb:
                x = -1 * xdiff/maxdiff
            elif b > lastb:
                x = 1 * xdiff/maxdiff
            if ydiff == 0:
                y = 0
            elif a < lasta:
                y = 1 * ydiff/maxdiff
            elif a > lasta:
                y = -1 * ydiff/maxdiff
            self.vector = (x,y)
        return self.vector
# ######################################################
class Controller():
    def __init__(self,rootWidget,useKeyboard=True,useAccelerometer=True,useJoystick=True,useTouchWidget=False,widget=None):
        self.keyboard = KeyboardHandler(active=useKeyboard, rootWidget=rootWidget, parent=self)
        self.touchWidget = TouchWidgetHandler(active=useTouchWidget,widget=widget,parent=self)
        self.accControl = AccelerometerHandler(active=useAccelerometer,rootWidget=rootWidget,parent=self)
        self.joystick = JoystickHandler(active=useJoystick, parent=self)
        self.vector = (0,0)
        self.pos =  (0,0)
        self.lastVector = self.vector
        self.enabled = False
# ------------------------------------------------------    
    def get_vector(self):
        v = (0,0)
        if self.keyboard.active and self.keyboard.hasPrecedence:
            v = self.keyboard.get_vector()
        elif self.joystick.active and self.joystick.hasPrecedence:
            v = self.joystick.get_vector()
        elif self.touchWidget.active and self.touchWidget.hasPrecedence:
            v = self.touchWidget.get_vector()
        elif self.accControl.active:
            v = self.accControl.get_vector()
        self.vector = v
        return v
# ------------------------------------------------------    
    def set_vector(self,v):
        Logger.debug('set_vector: {}'.format(v))
        self.vector = v
# ------------------------------------------------------
    def set_widget(self,widget):
        self.touchWidget.set_widget(widget)
# ------------------------------------------------------ 
    def enable(self):
        self.enabled = True
        self.vector = (0,0)
        if self.keyboard.active:
            self.keyboard.activate()
        if self.accControl.active:
            self.accControl.init_value()
# ------------------------------------------------------ 
    def disable(self):
        self.enabled = False       