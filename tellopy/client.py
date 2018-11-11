#!/usr/bin/env python3

import socket
import numpy as np
from .object_detector.server import Server

class Client:

    HOST = Server.HOST
    PORT = Server.PORT
    BUFFER_SIZE = Server.BUFFER_SIZE

    @property
    def addr(self):
        return (self.HOST, self.PORT)

    def socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_image_for_processing(self, data):
        with self.socket() as sock:
            sock.connect(self.addr)
            msg = data.tobytes()
            self._send(sock, msg)
            return self._recv(sock)

    def _send(self, sock, msg):
        print("sending %s bytes"%len(msg))
        sent = 0
        while sent < len(msg):
            sent += sock.sendto(msg[sent:sent+self.BUFFER_SIZE], self.addr)
        sock.sendto(b'\x00', self.addr)

    def _recv(self, sock):
        byts = b''
        while True:
            b = sock.recv(self.BUFFER_SIZE)
            byts += b
            if not b or len(b) < self.BUFFER_SIZE:
                break
        # We always send one byte too many
        return np.frombuffer(byts[:-1], dtype=np.uint8)
