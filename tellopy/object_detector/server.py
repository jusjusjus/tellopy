
import socket

class Server(socket.socket):

    HOST = '127.0.0.1'
    PORT = 65401
    BUFFER_SIZE = 1024

    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(self.addr)
        self.listen()

    def __del__(self):
        self.shutdown(socket.SHUT_RDWR)
        self.close()

    @property
    def addr(self):
        return (self.HOST, self.PORT)

    def accept(self):
        conn, addr = super().accept()
        with conn:
            print('Connected by', addr)
            byts = b''
            while True:
                b = conn.recv(self.BUFFER_SIZE)
                byts += b
                if not b or len(b) < self.BUFFER_SIZE:
                    break
            byts = byts[:-1]
            print("recieved %s bytes"%len(byts))

            print("sending back to %s"%str(addr))
            sent = 0
            while sent<len(byts):
                sent += conn.sendto(byts[sent:sent+self.BUFFER_SIZE], addr)
            conn.sendto(b'\x00', addr)

    def listen(self):
        super().listen()
        while True:
            self.accept()
