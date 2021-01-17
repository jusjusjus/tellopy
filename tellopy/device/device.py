from .command_socket import CommandSocket
from .command import Command


class Device:

    def __init__(self, socket):
        self.socket = socket

    @classmethod
    def init(cls, *args, **kwargs):
        socket = CommandSocket()
        socket.init()
        return cls(socket, *args, **kwargs)

    def takeoff(self):
        self.socket.send(Command.takeoff)

    def land(self):
        self.socket.send(Command.land)

    def streamon(self):
        self.socket.send(Command.streamon)

    def streamoff(self):
        self.socket.send(Command.streamoff)

    def forward(self, distance: int = 30):
        cmd = Command.forward(distance)
        self.socket.send(cmd)

    def back(self, distance: int = 30):
        cmd = Command.back(distance)
        self.socket.send(cmd)

    def up(self, distance: int = 30):
        cmd = Command.up(distance)
        self.socket.send(cmd)

    def down(self, distance: int = 30):
        cmd = Command.down(distance)
        self.socket.send(cmd)

    def flip(self, direction: str = 'b'):
        cmd = Command.flip(direction)
        self.socket.send(cmd)

    def rotate_ccw(self, degrees: int = 45):
        cmd = Command.ccw(degrees)
        self.socket.send(cmd)

    def rotate_cw(self, degrees: int = 45):
        cmd = Command.cw(degrees)
        self.socket.send(cmd)
