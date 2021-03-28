from kivy.logger import Logger
import traceback
from jnius import autoclass

# ######################################################
class AndroidAudioClip():

    AudioAttributes = autoclass('android.media.AudioAttributes')
    AABuilder = autoclass('android.media.AudioAttributes$Builder')
    MediaPlayer = autoclass('android.media.MediaPlayer')
# ------------------------------------------------------
    def __init__(self, source, loop=False, *args):
        self.load(source=source, loop=loop, *args)    
# ------------------------------------------------------    
    def load(self, source, loop, *args):
        self.mPlayer = self.MediaPlayer()           
        self.mPlayer.setDataSource(source)
       #Logger.debug('READ THIS: loading {} with loop={}'.format(source,loop))
        self.mPlayer.setLooping(loop)
        builder = self.AABuilder()
        builder.setUsage(self.AudioAttributes.USAGE_GAME)
        builder.setContentType(self.AudioAttributes.CONTENT_TYPE_SONIFICATION)
        attrib = builder.build()
        self.mPlayer.setAudioAttributes(attrib)
        self.mPlayer.prepare()
# ------------------------------------------------------
    def play(self):
        item = True
        # try:
        #     self.mPlayer.prepare()
        # except Exception:
        #     pass
        try:
            self.mPlayer.start()
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: start() failed')
            item = False
        if item:
           #Logger.debug('READ THIS: start() succeeded')
        return item
 # ------------------------------------------------------       
    def release(self):
        item = True
        try:
            self.mPlayer.release()
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: release() failed')
            item = False   
        return item         
# ------------------------------------------------------
    def stop(self):
        item = True
        try: 
            self.mPlayer.pause()
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: pause() failed')
            item = False
        if item:
           #Logger.debug('READ THIS: pause() succeeded.Trying seekto:')
        try:
            self.mPlayer.seekTo(0)
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: seekTo(0) failed')
            item = False  
        if item:
           #Logger.debug('READ THIS: seekTo(0) succeed') 
        return item                 
# ------------------------------------------------------
    def pause(self):
        item = True
        try: 
            self.mPlayer.pause()
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: pause() failed')
            item = False
        if item:
           #Logger.debug('READ THIS: pause() succeeded.')               
        return item                    
# ------------------------------------------------------
    def isPlaying(self):
        try:
            result = self.mPlayer.isPlaying()  
        except Exception:
            traceback.print_exc()
           #Logger.debug('READ THIS: couldn'' get isPlaying')
            result = False
       #Logger.debug('READ THIS: isPlaying={}'.format(result))
        return result      
# ------------------------------------------------------
    def __del__(self):
        self.release()
        try:
            super().__del__()
        except Exception:
            pass