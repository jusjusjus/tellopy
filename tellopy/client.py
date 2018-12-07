
import socket
import itertools
from .object_detector.server import Server
from .object_detector.pickle_protocol import PickleProtocol


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
