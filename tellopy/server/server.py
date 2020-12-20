import socket
from .pickle_protocol import PickleProtocol


class Server:

    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

    @classmethod
    def addr(self):
        return (self.HOST, self.PORT)

    def socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        with self.socket() as sock:
            sock.bind(self.addr())
            sock.listen()
            while True:
                conn, addr = sock.accept()
                self.serve(conn, addr)

    def _serve(self, conn):
        with conn:
            protocol = PickleProtocol(conn)
            while True:
                obj = protocol.recv()
                print("received", obj)
                protocol.send(obj)

    def serve(self, conn, addr):
        try:
            print('Connected by', addr)
            self._serve(conn)
        except ConnectionResetError as e:
            print(e)
