import numpy as np
import cv2
import time
import datetime
from threading import Thread

"""
MotionDetection Class, allows to detect camera motions:
    path: where you want to save your files
    video_source: numeric value of camera chosen (begining with 0)
    video_size: string of the resolution of video (ie '1080p')
    threshold: 0 very sensible ; 100000 not sensible at all
    time_interval: time between records in second
    recording_time: duration of the video recorded in second
    show_camera: boolean to show the camera capture
    show_mask: boolean to show the movement mask
    debug: boolean to show if you want to print the values of the noise
"""

### on quitte avec la touche Entrée.

class MotionDetection(object):
    is_recording = False
    time_counter = 0

    # Standard Video Dimensions Sizes
    STD_DIMENSIONS = {
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }

    def __init__(self, path, video_source, video_size, frame_rate, threshold, time_interval, recording_time, show_camera, show_mask, debug):
        self.video_source = video_source                # Source of the video
        self.video_size = video_size                    # Size of video
        self.get_dimensions(video_size)                 # Width and Height of camera
        self.threshold = threshold                      # Max noise threshold
        self.frame_rate = frame_rate                    # Frame rate of the output video
        self.time_interval = time_interval              # Time interval between records in seconds
        self.recording_time = recording_time            # Duration of the video recorded if motion detected
        self.path = path                                # Recorded file saving path
        self.show_camera = show_camera
        self.show_mask = show_mask
        self.debug = debug
        self.record = True # ajout d'une propriété afin de bloquer temporairement tout enregistrement.
        self.arretProgramme = False # ajout d'un propriété afin de demander l'extinction dans un thread, sans l'appui sur une touche.

        # Initializing components
        self.cap = cv2.VideoCapture(video_source)
        self.sub = cv2.createBackgroundSubtractorMOG2()
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

        # Preparing the windows
        if self.show_camera:
            cv2.namedWindow('Motion Detection', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Motion Detection', 640, 420)

        if self.show_mask:
            cv2.namedWindow('Motion Mask', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Motion Mask', 640, 420)

    def get_dimensions(self, video_size):
        self.width, self.height = self.STD_DIMENSIONS['480p']
        if video_size in self.STD_DIMENSIONS:
            self.width, self.height = self.STD_DIMENSIONS[video_size]

    def start(self):
        self.time_counter = time.time()
        print("Camera detected! Size: " + str(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) + 'x' + str(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print("Motion Detection activated. Waiting for motion...")
        while (True):
            # Reading the frame
            ret, frame = self.cap.read()
            if self.show_camera:
                cv2.imshow("Motion Detection", frame)
            else :
                try :
                    cv2.destroyWindow("Motion Detection")
                except :
                    True

            # optimisation si seul l'affichage est souhaitée et aucune détection de mouvement
            if self.record :
                # Creating the mask
                blur = cv2.GaussianBlur(frame, (19, 19), 0)
                mask = self.sub.apply(blur)
                if self.show_mask:
                    cv2.imshow("Motion Mask",mask)

                # Creating numpy histogram to analyse the noise of the pixels
                img_temp = np.ones(frame.shape, dtype="uint8") * 255
                img_temp_and = cv2.bitwise_and(img_temp, img_temp, mask=mask)
                img_temp_and_bgr = cv2.cvtColor(img_temp_and, cv2.COLOR_BGR2GRAY)
                hist, bins = np.histogram(img_temp_and_bgr.ravel(), 256, [0, 256])
                if self.debug:
                    print("Threshold =", self.threshold, ", Noise = ", hist[255], )

                # Testing if the histogram is greater than the threshold configured
                # Launching the recording thread
                if hist[255] > self.threshold and not self.is_recording and time.time() - self.time_counter > self.time_interval :
                    print("Motion detected! Recording video...")
                    self.is_recording = True
                    if not self.show_mask and not self.show_camera:
                        self.record_video()
                    else:
                        record_thread = Thread(target=self.record_video)
                        record_thread.start()
            if self.arretProgramme or cv2.waitKey(100) == 13:
                break
        try :
            record_thread.join()
            print("record thread finish")
        except :
            True
        self.cap.release()
        cv2.destroyAllWindows()

    def see(self,boolean):
        self.show_camera = bool(boolean)

    def recordOrNot(self,boolean) :
        self.record = bool(boolean)

    # Recording thread
    def record_video(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(self.path + '/' + date+'.avi', fourcc, self.frame_rate, self.STD_DIMENSIONS[self.video_size])
        time_counter = time.time()
        while time.time() - time_counter < self.recording_time and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret == True:
                out.write(frame)
            else:
                break
            cv2.waitKey(int(self.recording_time / self.frame_rate*100))
        print("Video recorded: " + self.path + '/' + date + '.mp4')
        self.time_counter = time.time()
        self.is_recording = False

    def end(self):
        self.arretProgramme = True
        print("Fin programmée")
        

if __name__ == "__main__" :
    ### variables : (path, video_source, video_size, frame_rate, threshold, time_interval, recording_time, show_camera, show_mask, debug)
    MD = MotionDetection("test", 1, '480p', 24.0, 20000, 0, 15, True, False, False)
    MD.start()
    MD.end()
