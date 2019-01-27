
import pickle
import numpy as np

class PickleProtocol:

    def __init__(self, conn):
        self.conn = conn
        self.data = b''

    def send(self, obj):
        msg = pickle.dumps(obj)
        msg = self.prefix_length(msg)
        self.conn.sendall(msg)

    def recv(self):
        byts = self.read_bytes(8)
        num_bytes = np.frombuffer(byts, count=1, dtype=np.uint64)[0]
        msg = self.read_bytes(num_bytes)
        obj = pickle.loads(msg)
        return obj

    @staticmethod
    def prefix_length(msg):
        return np.uint64(len(msg)).tobytes() + msg

    def _recv(self):
        self.data += self.conn.recv(1024)

    def read_bytes(self, n):
        while len(self.data) < n:
            self._recv()
        byts = self.data[:n]
        self.data = self.data[n:]
        return byts
