#https://github.com/ZelouiixDev/CameraMotionDetection
import time,os
from CameraMotionDetection import *

# Instanciating the class
videosDir = "videos"
if not os.path.exists(videosDir):
    os.makedirs(videosDir)
MD = MotionDetection(videosDir, 0, '420p', 12.0, 100000, 3, 3, True, True, False)

# Starting detection
MD.start()

# Stopping détection
MD.end()
