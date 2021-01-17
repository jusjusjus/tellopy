from .controller import Controller
from .command import Command


class Device:

    def __init__(self, device):
        self.device = device

    def takeoff(self):
        self.send('takeoff')

    def land(self):
        self.send('land')

    def rotate_cw(self):
        self.send('cw 45')

    def rotate_ccw(self):
        self.send('ccw 45')

    def send(self, string):
        command = Command(string)
        self.device.send(command)

    @classmethod
    def init(cls, *args, **kwargs):
        controller = Controller() 
        controller.init()
        return cls(controller, *args, **kwargs)
