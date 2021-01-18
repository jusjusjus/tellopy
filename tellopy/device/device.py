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

    def stop(self):
        self.socket.send(Command.stop)

    def command(self):
        self.socket.send(Command.command)

    def emergency(self):
        self.socket.send(Command.emergency)

    def streamon(self):
        self.socket.send(Command.streamon)

    def streamoff(self):
        self.socket.send(Command.streamoff)

    def forward(self, distance: int = 30):
        cmd = Command.forward(distance)  # type: ignore
        self.socket.send(cmd)

    def right(self, distance: int = 30):
        cmd = Command.right(distance)  # type: ignore
        self.socket.send(cmd)

    def left(self, distance: int = 30):
        cmd = Command.left(distance)  # type: ignore
        self.socket.send(cmd)

    def back(self, distance: int = 30):
        cmd = Command.back(distance)  # type: ignore
        self.socket.send(cmd)

    def up(self, distance: int = 30):
        cmd = Command.up(distance)  # type: ignore
        self.socket.send(cmd)

    def down(self, distance: int = 30):
        cmd = Command.down(distance)  # type: ignore
        self.socket.send(cmd)

    def flip(self, direction: str = 'b'):
        cmd = Command.flip(direction)  # type: ignore
        self.socket.send(cmd)

    def ccw(self, degrees: int = 45):
        cmd = Command.ccw(degrees)  # type: ignore
        self.socket.send(cmd)

    def cw(self, degrees: int = 45):
        cmd = Command.cw(degrees)  # type: ignore
        self.socket.send(cmd)
