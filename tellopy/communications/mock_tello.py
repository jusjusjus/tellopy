
import re
import socket
from threading import Thread
from subprocess import check_output

from typing import Tuple, List, Dict, Any, Callable

# Set the drone to listen to 'loopback'
from .config import Config
Config.drone_ip = '127.0.0.1'
Config.control_port = 8889

class TelloProtocol:

    def __init__(self, conn):
        self.conn = conn
        self.data = b''

    def send(self, txt):
        self.conn.sendall(txt)

    def recv(self):
        return self.conn.recvfrom(128)


class MockTello(Thread):

    HOST: str = Config.drone_ip
    PORT: int = Config.control_port
    cmd_with_params_re = re.compile(r'[a-zA-Z]*. \d')

    def __init__(self):
        super().__init__(target=self.listen)
        self.deamon = True
        self.drone_initialized: bool = False
        self.stream_is_on: bool = False
        # these are the actions processed
        self.actions: Dict[str, Callable] = {
            'command': self.init_tello,
            'streamon': self.streamon
        }

    @classmethod
    def addr(cls) -> Tuple[str, int]:
        return (cls.HOST, cls.PORT)

    def socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        with self.socket() as sock:
            sock.bind(self.addr())
            sock.listen()
            while True:
                conn, addr = sock.accept()
                self.serve(conn, addr)

    def streamon(self) -> bytes:
        if not self.drone_initialized or self.stream_is_on:
            return Config.ERROR

        def ffmpeg_stream():
            check_output(['ffmpeg',
                '-i', '/dev/video0',
                '-s', '320x240', # video size in px
                '-r', '5', # frames per second
                '-f', 'mpegts', # MPEG transport stream
                'udp://%s:%s'%(Config.drone_ip, Config.video_port)])

        self.video = Thread(target=ffmpeg_stream)
        self.video.daemon = True
        self.video.start()
        return Config.OK

    def init_tello(self) -> bytes:
        """initializes tello, returns `Config.ERROR` if already initialized"""
        if self.drone_initialized:
            return Config.ERROR
        else:
            self.drone_initialized = True
            print("Mock Drone initialized")
            return Config.OK

    def match_cmd_with_params(self, msg: str) -> Tuple[str, int]:
        matches = self.cmd_with_params_re.match(msg)
        assert matches is not None
        match = matches.group()
        assert len(match) == len(msg)
        cmd, val = match.split(' ')
        return cmd, int(val)

    def process(self, msg: bytes) -> bytes:
        """process the message and generate response"""
        try:
            msg_str = msg.decode('utf-8').rstrip('\n').rstrip('\r')
        except UnicodeDecodeError:
            raise BrokenPipeError
        try:
            print("process for single-command action", msg_str)
            return self.actions[msg_str]()
        except KeyError:
            print("process for command with params", msg_str)
            # process commands with parameters
            try:
                cmd, val = self.match_cmd_with_params(msg_str)
                return self.actions[cmd](int(val))
            except (AttributeError, AssertionError) as err:
                print(err)
                return Config.ERROR

    def _serve(self, conn):
        while True:
            try:
                msg, addr = conn.recvfrom(128)
                response = self.process(msg)
                conn.sendall(response)
            except BrokenPipeError:
                raise ConnectionResetError("Connection lost")

    def serve(self, conn, addr):
        try:
            with conn:
                print('Connected by', addr)
                self._serve(conn)
        except ConnectionResetError as e:
            print(e)
