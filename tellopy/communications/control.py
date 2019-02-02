
import socket
from threading import Thread

from .config import Config
from .abort_timer import AbortTimer

class Control:

    valid_commands = [
        # flight controls
        b'back 100',
        b'forward 100',
        b'down 100',
        b'up 100',
        b'land',
        b'takeoff',
        b'ccw 45',
        b'cw 45',
        b'flip b',
        # Turn on video stream on port 11111
        b'streamon',
        # Turn video stream off
        b'streamoff',
        # initialize tello
        b'command',
    ]

    drone_addr = (Config.drone_ip, Config.control_port)
    response_timeout = 0.5

    def __init__(self):
        self.initialized = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def get_my_own_ip():
        dummy_host = (Config.drone_ip, Config.controller_port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(dummy_host)
            ip = sock.getsockname()[0]
        assert ip.startswith(Config.drone_ip[:10]), "Please connect to the tello (current ip: %s)"%ip
        return ip
       
    def init(self):
        addr = (self.get_my_own_ip(), Config.controller_port)
        print('bind', addr, 'and connect to', self.drone_addr)
        try:
            self.sock.bind(addr)
            self.sock.connect(self.drone_addr)
        except OSError as e:
            msg = "while binding %s:%s, "%addr + str(e)
            raise OSError(msg)
        response = self.send(b'command')
        self.initialized = True#response == Config.OK
        return self

    def wait_for_response(self):

        response = None

        def listen():
            while True:
                try:
                    response, ip = self.sock.recvfrom(128)
                    break
                except Exception as e:
                    print("recv_thread Exception '%s', exiting.."%e)
                    response = Config.ERROR
                    break

        receiver = Thread(target=listen)
        receiver.deamon = True
        receiver.start()
        receiver.join(self.response_timeout)
        # receiver timed out if thread is still alive (maybe the connection
        # broke?)
        return Config.TIMEOUT if receiver.isAlive() else response

    def check_command(self, cmd: bytes):
        assert self.initialized or cmd == b'command'
        assert cmd in self.valid_commands, "%s not in %s"%(cmd, self.valid_commands)

    def send(self, cmd: bytes):
        print('try sending', cmd, 'to', self.drone_addr)
        self.check_command(cmd)
        self.sock.sendall(cmd)#, self.drone_addr)
        response = self.wait_for_response()
        print('response', response)
        return response
