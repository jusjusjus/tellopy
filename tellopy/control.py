import socket
import logging
import threading

_OK = 'ok'
_ERROR = 'error'


class AbortTimer(threading.Timer):

    def __init__(self, timeout):
        super().__init__(timeout, self.set_abort)
        self.abort = False
        self.start()

    def set_abort(self):
        self.abort = True


class Receiver(threading.Thread):

    def __init__(self, sock):
        self.sock = sock
        self.reset()
        super().__init__(target=self._receive)
        self.deamon = True
        self.start()

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, r):
        self._response = r.decode('utf-8')

    def reset(self):
        self._response = None

    def _receive(self):
        self.info("start listening to (%s, %s)" % self.addr)
        while True:
            try:
                self.response, ip = self.recvfrom(256)
                self.info('recv msg %s from %s' % (self.response, ip))
            except Exception as e:
                self.error("recv_thread Exception %s, exiting.." % e)
                break

    def info(self, *args, **kwargs):
        self.sock.info(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.sock.error(*args, **kwargs)

    @property
    def addr(self):
        return self.sock.addr

    def recvfrom(self, n):
        return self.sock.recvfrom(n)


class UDPSocket(socket.socket):

    logger = logging.getLogger(name='UDPSocket')
    _command_timeout = 0.5
    name = ''
    _listen = False

    def __init__(self, ip, port, name='', listen=True):
        assert isinstance(ip, str) and isinstance(port, int) \
            and isinstance(name, str) and isinstance(listen, bool)
        self.name = name
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.bind()
        self.listen = listen

    @property
    def listen(self):
        return self._listen

    @listen.setter
    def listen(self, listen):
        self._listen = listen
        self.receiver = Receiver(self) if listen else None

    def __del__(self):
        self.close()

    def bind(self):
        try:
            super().bind(self.addr)
        except OSError as e:
            msg = "while binding %s, " % str(self.addr) + str(e)
            raise OSError(msg)

    def info(self, msg):
        self.logger.info(self.name + ': ' + msg)

    def error(self, msg):
        self.logger.error(self.name + ': ' + msg)

    def _wait_for_response(self):
        timer = AbortTimer(self._command_timeout)
        try:
            while self.receiver.response is None:
                if timer.abort:
                    raise RuntimeError('no response received!')
            response = self.receiver.response
            assert response in (_OK, _ERROR), "unknown response %s" % response
        except RuntimeError as e:
            self.error(str(e))
            response = _ERROR
        timer.cancel()
        self.receiver.reset()
        return response

    def send(self, addr, msg):
        self.info("send msg %s to %s from %s" % (msg, addr, self.addr))
        msg = msg if isinstance(msg, bytes) else msg.encode('utf-8')
        self.sendto(msg, addr)
        return self._wait_for_response() if self.listen else _OK


class CommandControl:

    logger = logging.getLogger(name='CommandControl')
    _local_ip = '192.168.10.2'
    _cmd_port = 8889
    _tello_ip = '192.168.10.1'
    _tello_addr = ('192.168.10.1', 8889)

    def __init__(self):
        self.cmd_sock = UDPSocket(
            self._local_ip, self._cmd_port, name='cmd', listen=True)
        msg = self.send_command('command', assert_ok=True)
        if msg != _OK:
            raise RuntimeError(f"Received {msg}. "
                               "Tello rejected attempt to enter command mode")

    def send_command(self, command, assert_ok=False):
        try:
            msg = self.cmd_sock.send(self._tello_addr, command)
        except Exception as e:
            msg = str(e)
        info = "sent %s, recv'd %s" % (command, msg)
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
