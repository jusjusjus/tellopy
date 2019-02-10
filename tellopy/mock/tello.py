
import re
from socket import socket, AF_INET, SOCK_STREAM
import logging
from threading import Thread
from subprocess import check_output

from typing import Tuple, List, Dict, Any, Callable

# Set the drone to listen to 'loopback'
from .video import Video
from ..communications.config import Config
Config.drone_ip = '127.0.0.1'
Config.control_port = 8889
Config.controller_port = 33333
Config.socket_config = SOCK_STREAM

class Tello(Thread):

    cmd_with_params_re = re.compile(r'[a-zA-Z]*. \d')
    logger = logging.getLogger(name="MockTello")

    def __init__(self):
        super().__init__(target=self.listen)
        self.deamon = True
        self.drone_initialized: bool = False
        self.stream_is_on: bool = False
        # these are the actions processed
        self.actions: Dict[str, Callable] = {
            'command': self.init_tello,
            'streamon': self.streamon,
            'streamoff': self.streamoff
        }

    def listen(self):
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.bind((Config.drone_ip, Config.control_port))
            sock.listen()
            while True:
                conn, addr = sock.accept()
                self.serve(conn, addr)

    def streamoff(self) -> bytes:
        if not self.stream_is_on:
            return Config.ERROR
        self.video.stop()
        self.stream_is_on = False
        return Config.OK

    def streamon(self) -> bytes:
        if not self.drone_initialized or self.stream_is_on:
            return Config.ERROR
        self.video = Video.run_in_thread()
        self.stream_is_on = True
        return Config.OK

    def init_tello(self) -> bytes:
        """initializes tello, returns `Config.ERROR` if already initialized"""
        if self.drone_initialized:
            return Config.ERROR
        else:
            self.drone_initialized = True
            self.logger.info("Mock Drone initialized")
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
            self.logger.info("process for single-command action '%s'"%msg_str)
            return self.actions[msg_str]()
        except KeyError:
            self.logger.info("process for command with params '%s'"%msg_str)
            # process commands with parameters
            try:
                cmd, val = self.match_cmd_with_params(msg_str)
                return self.actions[cmd](int(val))
            except (AttributeError, AssertionError) as err:
                self.logger.error(err)
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
                self.logger.info("Connected by '%s'"%str(addr))
                self._serve(conn)
        except ConnectionResetError as err:
            self.logger.error(err)
