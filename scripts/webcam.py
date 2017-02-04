import cv2
from threading import Thread

class Webcam:
 
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
        self.current_frame = self.video_capture.read()[1]

        self.webcamON = True

    # create thread for capturing images
    def start(self):
        Thread(target=self._update_frame, args=()).start()

    def stop(self):
        self.webcamON = False
 
    def _update_frame(self):
        while(self.webcamON):
            self.current_frame = self.video_capture.read()[1]
                 
    # get the current frame
    def get_current_frame(self):
        return self.current_frame
