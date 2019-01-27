
import socket
from .server import Server
from .pickle_protocol import PickleProtocol


class Client:

    def socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, sock):
        sock.connect(Server.addr())

    @classmethod
    def send(cls, sock, obj):
        protocol = PickleProtocol(sock)
        protocol.send(obj)
        return protocol.recv()
