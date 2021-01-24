import numpy as np
from PyQt5.QtWidgets import QWidget
from time import sleep

class RemoteControl(QWidget):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.setMouseTracking(True)

    def size(self):
        size = super().size()
        return np.array([size.width(), size.height()], np.float32)

    def mouseMoveEvent(self, event):
        pos = self.position_from_event(event)
        a, b = (100 * pos).astype(int).tolist()
        print(self.device.rc(a, b, 0, 0))

    def position_from_event(self, event):
        pos = 2 * np.array([event.x(), event.y()], dtype=np.float32) / self.size()
        return np.array([pos[0] - 1, 1 - pos[1]], dtype=np.float32)
