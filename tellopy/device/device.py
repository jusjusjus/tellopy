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
        return self.socket.send(Command.takeoff)

    def land(self):
        return self.socket.send(Command.land)

    def stop(self):
        return self.socket.send(Command.stop)

    def command(self):
        return self.socket.send(Command.command)

    def emergency(self):
        return self.socket.send(Command.emergency)

    def streamon(self):
        return self.socket.send(Command.streamon)

    def streamoff(self):
        return self.socket.send(Command.streamoff)

    def forward(self, distance: int = 30):
        cmd = Command.forward(distance)  # type: ignore
        return self.socket.send(cmd)

    def right(self, distance: int = 30):
        cmd = Command.right(distance)  # type: ignore
        return self.socket.send(cmd)

    def left(self, distance: int = 30):
        cmd = Command.left(distance)  # type: ignore
        return self.socket.send(cmd)

    def back(self, distance: int = 30):
        cmd = Command.back(distance)  # type: ignore
        return self.socket.send(cmd)

    def up(self, distance: int = 30):
        cmd = Command.up(distance)  # type: ignore
        return self.socket.send(cmd)

    def down(self, distance: int = 30):
        cmd = Command.down(distance)  # type: ignore
        return self.socket.send(cmd)

    def flip(self, direction: str = 'b'):
        cmd = Command.flip(direction)  # type: ignore
        return self.socket.send(cmd)

    def ccw(self, degrees: int = 45):
        cmd = Command.ccw(degrees)  # type: ignore
        return self.socket.send(cmd)

    def cw(self, degrees: int = 45):
        cmd = Command.cw(degrees)  # type: ignore
        return self.socket.send(cmd)

    def rc(self, right: int, forward: int, up: int, yaw: int):
        cmd = Command.cw(right, forward, up, yaw)  # type: ignore
        return self.socket.send(cmd)
