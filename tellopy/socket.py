
from .udp_socket import UDPSocket, Receiver
import numpy as np


class ControlReceiver(Receiver):

    def process_response(self):
        if len(self.response) == 35:
            try:
                data = np.frombuffer(self.response[1:], dtype=np.uint8)
                if not hasattr(self, 'last_data'):
                    self.last_data = data
                for i, (x, y) in enumerate(zip(data, self.last_data)):
                    if x != y:
                        print(i, x)
                # print(', '.join(map(str, data)))
                self.last_data = data.copy()
            except Exception as e:
                print('invalid response (%s)'%str(e), self.response)
        # if len(self.response) == 270:
        #     try:
        #         data = np.frombuffer(self.response[2:], dtype=np.int32)
        #         if not hasattr(self, 'last_data'):
        #             self.last_data = data
        #         for i, (x, y) in enumerate(zip(data, self.last_data)):
        #             if x != y:
        #                 print(i, x)
        #         # print(', '.join(map(str, data)))
        #         self.last_data = data.copy()
        #     except Exception as e:
        #         print('invalid response (%s)'%str(e), self.response)


class RTPSocket(UDPSocket):
    host_port = 7777
    remote_addr = ('192.168.10.1', 7777)
    def __init__(self, logfile=None):
        super().__init__(self.host_port, listen=True, name="RTPSocket", logfile=logfile)

class CommandSocket(UDPSocket):
    host_port = 8889
    remote_addr = ('192.168.10.1', 8889)
    def __init__(self, logfile=None):
        super().__init__(self.host_port, listen=True, name="CommandSocket", logfile=logfile)

    def init_tello(self):
        """initialize Tello"""
        buf = "conn_req:".encode('utf-8')
        buf += np.uint16(RTPSocket.host_port).tobytes()
        assert "63 6f 6e 6e 5f 72 65 71 3a 61 1e" == ' '.join(str(k)+str(i) for k, i in zip(buf.hex()[::2], buf.hex()[1::2]))
        self.send(self.remote_addr, buf)

    @property
    def listen(self):
        return self._listen

    @listen.setter
    def listen(self, l):
        self._listen = l
        self.receiver = ControlReceiver(self, logfile=self.logfile) if l else None
