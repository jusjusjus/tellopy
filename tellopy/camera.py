
import cv2
import time
import threading
import numpy as np

class Camera:

    FLAG = cv2.COLOR_RGB2BGR
    image = None
    fps = 30.0

    def __init__(self, slot=0, show=False):
        self.show = show
        self.slot = slot
        self.open()
        self.reader = threading.Thread(target=self.read)
        self.reader.start()
        if show:
            self.teller = threading.Thread(target=self.play)
            self.teller.start()

    def open(self):
        self.cam = cv2.VideoCapture(self.slot)
        if not self.cam.isOpened():
            self.cam.open(0)

    def close(self):
        self.cam.release()
        cv2.destroyAllWindows()

    def __del__(self):
        self.close()

    def _read(self):
        success, img = self.cam.read()
        assert success == True
        return cv2.cvtColor(img, self.FLAG) if self.FLAG else self.FLAG

    def read(self):
        while True:
            self.image = self._read()

    def _show_image(self):
        if self.image is None: return
        cv2.imshow('display', self.image)

    def play(self):
        while self.show:
            time.sleep(1/self.fps)
            self._show_image()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
