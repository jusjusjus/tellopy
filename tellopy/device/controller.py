
import socket
from threading import Thread

from .config import Config
from .command import Command


class Controller:

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
        # Turn on video stream
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
        self.sock = socket.socket(socket.AF_INET, Config.socket_config)

    @staticmethod
    def get_my_own_ip():
        dummy_host = (Config.drone_ip, Config.controller_port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(dummy_host)
            ip = sock.getsockname()[0]

        assert ip.startswith(Config.drone_ip[:10]),f"""
        Please connect to the tello drone (current IP is {ip})"""
        return ip

    def init(self):
        addr = (self.get_my_own_ip(), Config.controller_port)
        print(f"bind {addr} and connect to {self.drone_addr}")
        try:
            self.sock.bind(addr)
            self.sock.connect(self.drone_addr)
        except OSError as e:
            raise OSError(f"Error while binding {addr}: {e}")

        init_command = Command('command')
        response = self.send(init_command)
        self.initialized = response == Config.OK
        return self

    def wait_for_response(self):

        def listen():
            while True:
                try:
                    self._response, ip = self.sock.recvfrom(128)
                    break
                except Exception as e:
                    print(f"recv_thread Exception '{e}', exiting..")
                    self._response = Config.ERROR
                    break

        receiver = Thread(target=listen)
        receiver.deamon = True
        self._response = None
        receiver.start()
        receiver.join(self.response_timeout)
        # receiver timed out if is still alive (maybe the connection broke?)
        return Config.TIMEOUT if receiver.isAlive() else self._response

    def check_command(self, cmd: Command):
        assert self.initialized or cmd.is_init_command()

    def send(self, cmd: Command):
        self.check_command(cmd)
        self.sock.sendall(cmd.tobytes())
        response = self.wait_for_response()
        print(f"{self.drone_addr} upon '{cmd}': {response}")
        return response
