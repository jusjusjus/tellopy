
import socket
import logging
import threading
from .config import _OK, _ERROR


class AbortTimer(threading.Timer):

    def __init__(self, timeout):
        super().__init__(timeout, self.set_abort)
        self.abort = False
        self.start()

    def set_abort(self):
        self.abort = True


class Receiver(threading.Thread):

    def __init__(self, sock, logfile=None):
        self.sock = sock
        self.reset()
        super().__init__(target=self._receive)
        self.deamon = True
        self.start()
        self.logfile = logfile
        self.msg_index = 0

    def log(self, d):
        if self.logfile:
            fname = 'log/'+self.logfile+'_%03i.bin'%self.msg_index
            with open(fname, 'wb') as f:
                f.write(d)
            self.msg_index += 1

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, r):
        try:
            self._response = r.decode('utf-8')
        except:
            self._response = r

    def reset(self):
        self._response = None
        
    def process_response(self):
        self.log(self.response)

    def _receive(self):
        self.info("start listening to (%s, %s)"%self.addr)
        while True:
            try:
                self.response, ip = self.recvfrom(1024)
                self.process_response()
                self.info('recv msg of length %s from %s'%(len(self.response), ip))
            except Exception as e:
                self.error("recv_thread Exception '%s', exiting.."%e)
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

    def __init__(self, port, ip=None, name='', listen=True, logfile=None):
        assert isinstance(ip, (str, type(None))) and isinstance(port, int) and isinstance(name, str) and isinstance(listen, bool)
        ip = ip or self.get_ip()
        self.name = name
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.bind()
        self.logfile = logfile
        self.listen = listen

    @staticmethod
    def get_ip():
        dummy_host = ('8.8.8.8', 53)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(dummy_host)
            ip = sock.getsockname()[0]
        assert ip.startswith('192.168.10'), "Please connect to the tello (current ip: %s)"%ip
        return ip

    @property
    def listen(self):
        return self._listen

    @listen.setter
    def listen(self, l):
        self._listen = l
        self.receiver = Receiver(self, logfile=self.logfile) if l else None

    def __del__(self):
        self.close()

    def bind(self):
        try:
            super().bind(self.addr)
        except OSError as e:
            msg = "while binding %s, "%str(self.addr) + str(e)
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
            assert response in (_OK, _ERROR), "unknown response %s"%response
        except RuntimeError as e:
            self.error(str(e))
            response = _ERROR
        timer.cancel()
        self.receiver.reset()
        return response

    def send(self, addr, msg, ack=False):
        self.info("send msg %s to %s from %s"%(msg, addr, self.addr))
        msg = msg if isinstance(msg, bytes) else msg.encode('utf-8')
        self.sendto(msg, addr)
        return self._wait_for_response() if ack and self.listen else _OK

