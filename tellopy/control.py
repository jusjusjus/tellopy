
import time
import socket
import logging
import threading

_OK = 'ok'
_ERROR = 'error'

class UDPSocket(socket.socket):

    logger = logging.getLogger(name='UDPSocket')
    _command_timeout = 0.5

    def __init__(self, ip, port):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.bind()
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        self.abort_flag = False

    def __del__(self):
        self.close()

    def bind(self):
        super().bind(self.addr)

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.recvfrom(256)
                self.logger.info('Received msg %s from %s'%(self.response, ip))
            except Exception:
                break

    def set_abort_flag(self):
        self.abort_flag = True

    def wait_for_response(self):
        timer = threading.Timer(self._command_timeout, self.set_abort_flag)
        timer.start()
        try:
            while self.response is None:
                if self.abort_flag is True:
                    raise RuntimeError('No response to command [%s, %s]'%(self.response, self.abort_flag))
            timer.cancel()
            response = self.response.decode('utf-8')
        except:
            self.logger.error("No response received!")
            timer.cancel()
            response = _OK
        self.response = None
        return response

    def send(self, addr, msg):
        self.logger.info("Sending '%s' to %s from %s"%(msg, addr, self.addr))
        self.abort_flag = False
        self.sendto(msg.encode('utf-8'), addr)
        return self.wait_for_response()


class Control:

    logger = logging.getLogger(name='Control')
    _local_ip = '192.168.10.2'
    _tello_addr = ('192.168.10.1', 8889)

    def __init__(self):
        self.abort_flag = False
        self.response = None
        self.port8889 = UDPSocket(self._local_ip, 8889)
        
        msg = self.send_command('command')
        if msg != _OK:
            raise RuntimeError('Received %s.  Tello rejected attempt to enter command mode'%msg)

    def send_command(self, command):
        return self.port8889.send(self._tello_addr, command)

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
