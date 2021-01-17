
import av
import numpy as np
from time import sleep
from threading import Thread
from .abort_timer import AbortTimer


def tensor_to_image(t):
    img = t.numpy()
    img = img.transpose(1, 2, 0)
    img = img * 255
    return img.astype(np.uint8)


class Video:

    def __init__(self, url):
        self.stop_signal_received = False
        self._frame = None
        self.url = url

    @property
    def container(self):
        try:
            return self._container
        except AttributeError:
            self._container = av.open(self.url)
            return self.container

    @staticmethod
    def _image_to_numpy(image):
        byts = image.tobytes()
        img = np.frombuffer(byts, dtype='u1')
        img.shape = (image.size[1], image.size[0], 3)
        return img

    @property
    def frame(self) -> np.ndarray:
        try:
            return self._image_to_numpy(self._frame.to_image())
        except AttributeError:
            return None

    def _read_frames_from_container(self):
        for self._frame in self.container.decode(video=0):
            if self.stop_signal_received:
                break

    def start(self, timeout=1.0, blocking=True):
        self.thread = Thread(target=self._read_frames_from_container)
        self.thread.daemon = True
        self.stop_signal_received = False
        self.thread.start()
        if blocking:
            timer = AbortTimer(timeout)
            while not timer.abort:
                if self.frame is None:
                    sleep(0.1)
                else:
                    break
            else:
                raise IOError

    def stop(self):
        self.stop_signal_received = True
        self.thread.join()
        del self.thread

    @property
    def running(self):
        return hasattr(self, 'thread')
