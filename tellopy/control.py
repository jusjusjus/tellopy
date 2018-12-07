
import logging
from .socket import UDPSocket
from .config import _OK, _ERROR

class CommandControl:

    logger = logging.getLogger(name='CommandControl')
    _local_ip = '192.168.10.2'
    _cmd_port = 8889
    _tello_ip = '192.168.10.1'
    _tello_addr = ('192.168.10.1', 8889)

    def __init__(self):
        self.cmd_sock = UDPSocket(self._local_ip, self._cmd_port, name='cmd', listen=True)
        msg = self.send_command('command', assert_ok=True)
        if msg != _OK:
            raise RuntimeError('Received %s.  Tello rejected attempt to enter command mode'%msg)

    def send_command(self, command, assert_ok=False):
        try:
            msg = self.cmd_sock.send(self._tello_addr, command)
        except Exception as e:
            msg = str(e)
        info = "sent %s, recv'd %s"%(command, msg)
        if assert_ok and msg == _ERROR:
            raise RuntimeError(info)
        else:
            self.cmd_sock.info(info)

    def land(self):
        return self.send_command('land')

    def move(self, direction, distance):
        distance = int(round(float(distance) * 100))
        return self.send_command('%s %s' % (direction, distance))

    def move_backward(self, distance):
        return self.move('back', distance)

    def move_down(self, distance):
        return self.move('down', distance)

    def move_forward(self, distance):
        return self.move('forward', distance)

    def move_left(self, distance):
        return self.move('left', distance)

    def move_right(self, distance):
        return self.move('right', distance)

    def move_up(self, distance):
        return self.move('up', distance)

    def takeoff(self):
        return self.send_command('takeoff')

    def rotate_cw(self, degrees):
        return self.send_command('cw %s' % degrees)

    def rotate_ccw(self, degrees):
        return self.send_command('ccw %s' % degrees)
