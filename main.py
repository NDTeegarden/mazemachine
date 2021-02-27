KIVY_NO_ARGS=1
import maze
from kivy.logger import Logger

__version__ = "0.2"

if __name__ == '__main__':
    Logger.info('main.py: Entering __main__')
    maze.MazeApp().run()