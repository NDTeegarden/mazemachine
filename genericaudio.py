from kivy.logger import Logger
from kivy.core.audio import SoundLoader
import traceback

# ######################################################
class GenericAudioClip():

# ------------------------------------------------------
    def __init__(self, source, loop=False, *args):
        self.load(source=source, loop=False, *args)    
# ------------------------------------------------------
    def load(self, source, loop=False, *args):
        item = True
        self.sound = None
        try:
            self.sound = SoundLoader.load(source, loop=loop)
        except Exception:
            traceback.print_exc()
            Logger.debug('{} load() failed'.format(self))
            item = False   
        return item  
# ------------------------------------------------------
    def play(self):
        item = True
        try:
            self.sound.play()
        except Exception:
            traceback.print_exc()
            Logger.debug('{} play() failed'.format(self))
            item = False
        finally:
            return item          
# ------------------------------------------------------    
    def release(self):
        item = True
        try:
            self.sound.unload()
        except Exception:
            traceback.print_exc()
            Logger.debug('{} release() failed'.format(self))
            item = False
        finally:
            return item   
 # ------------------------------------------------------   
    def pause(self):
        item = True
        try:
            pos = self.sound.get_pos()
        except Exception:
            traceback.print_exc()
            Logger.debug('{} pause() failed on get_pos()'.format(self))
            item = False
        finally:
            item = self.stop()
            try:
                self.seekTo(pos)
            except Exception:
                traceback.print_exc()
                Logger.debug('{} pause() failed on seekTop()'.format(self))
                item = False
            finally:
                return item                

# ------------------------------------------------------
    def stop(self):
        item = True
        try:
            self.sound.stop()
        except Exception:
            traceback.print_exc()
            Logger.debug('{} stop() failed'.format(self))
            item = False
        finally:
            return item   
# ------------------------------------------------------
    def isPlaying(self):
        result = False
        try:
            state = self.sound.state
        except Exception:
            traceback.print_exc()
            Logger.debug('{} stop() failed'.format(self))
            state = 'stop'  
        if state == 'play':
            result = True
        else:
            result = False
        return result  