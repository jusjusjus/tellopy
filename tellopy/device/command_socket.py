
from socket import socket, AF_INET
from threading import Thread

from .config import Config
from .command import Command

from ..utils import get_own_ip


class CommandSocket:

    drone_addr = (Config.drone_ip, Config.control_port)
    response_timeout = 0.5

    def __init__(self):
        self.initialized = False
        self.sock = socket(AF_INET, Config.socket_config)

    def send(self, cmd: Command):
        self.check_command(cmd)
        self.sock.sendall(cmd.tobytes())
        response = self.wait_for_response()
        print(f"{self.drone_addr} upon '{cmd}': {response}")
        return response

    def check_command(self, cmd: Command):
        assert self.initialized or cmd.is_init_command()

    def wait_for_response(self):
        receiver = Thread(target=self._listen)
        receiver.deamon = True
        self._response = None
        receiver.start()
        receiver.join(self.response_timeout)
        return self._response if not receiver.isAlive() else Config.TIMEOUT

    def init(self):
        ip = get_own_ip()
        assert ip.startswith(Config.drone_ip[:10]), f"""
        Please connect to the tello drone (current IP is {ip})"""
        addr = (ip, Config.controller_port)
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

    def _listen(self):
        while True:
            try:
                self._response, ip = self.sock.recvfrom(128)
                break
            except Exception as e:
                print(f"recv_thread Exception '{e}', exiting..")
                self._response = Config.ERROR
                break
