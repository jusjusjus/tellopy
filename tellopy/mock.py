
import time
import logging
import threading
import traceback

_OK = 'ok'
_ERROR = 'error'

class Socket:

    def sendto(self, msg, addr):
        print("Sending %s to %s"%(msg, addr))

class UDPSocket(Socket):

    logger = logging.getLogger(name='UDPSocket')
    _command_timeout = 0.5

    def __init__(self, ip, port):
        print("super().__init__(socket.AF_INET, socket.SOCK_DGRAM)")
        self.addr = (ip, port)
        self.bind()
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        self.abort_flag = False

    def __del__(self):
        print("self.close()")

    def bind(self):
        print("super().bind(self.addr)")

    def send(ip, port, command):
        print("Sending '%s' to %s:%s"(command, ip, port))
        return True

    def recvfrom(self, num_bytes):
        time.sleep(1.0)
        return num_bytes, ('0.0.0.0', 8888) 

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.recvfrom(256)
                self.logger.info('Received msg %s from %s'%(self.response, ip))
            except Exception:
                break

    def set_abort_flag(self):
        self.abort_flag = True

    def wait_for_response(self):
        timer = threading.Timer(self._command_timeout, self.set_abort_flag)
        timer.start()
        try:
            while self.response is None:
                if self.abort_flag is True:
                    raise RuntimeError('No response to command [%s, %s]'%(self.response, self.abort_flag))
            timer.cancel()
            response = self.response.decode('utf-8')
        except:
            self.logger.error("No response received!")
            timer.cancel()
            response = _OK
        self.response = None
        return response

    def send(self, addr, msg):
        self.logger.info("Sending '%s' to %s from %s"%(msg, addr, self.addr))
        self.abort_flag = False
        self.sendto(msg.encode('utf-8'), addr)
        return self.wait_for_response()


class Mock:

    logger = logging.getLogger(name='Control')
    _local_ip = '192.168.10.2'
    _tello_addr = ('192.168.10.1', 8889)

    def __init__(self):
        self.abort_flag = False
        self.response = None
        self.port8889 = UDPSocket(self._local_ip, 8889)
        
        msg = self.send_command('command')
        if msg != _OK:
            raise RuntimeError('Received %s.  Tello rejected attempt to enter command mode'%msg)

    def send_command(self, command):
        return self.port8889.send(self._tello_addr, command)

    def flip(self, direction):
        return self.send_command('flip %s' % direction)

    def get_battery(self):
        battery = self.send_command('battery?')
        try:
            battery = int(battery)
        except:
            pass
        return battery


    def get_flight_time(self):
        flight_time = self.send_command('time?')
        try:
            flight_time = int(flight_time)
        except:
            pass
        return flight_time

    def get_speed(self):
        speed = self.send_command('speed?')
        try:
            speed = round((float(speed) / 27.7778), 1)
        except:
            pass

        return speed

    def land(self):
        return self.send_command('land')

    def move(self, direction, distance):
        distance = int(round(float(distance) * 100))
        return self.send_command('%s %s' % (direction, distance))

    def move_backward(self, distance):
        return self.move('back', distance)

    def move_down(self, distance):
        return self.move('down', distance)

    def move_forward(self, distance):
        return self.move('forward', distance)

    def move_left(self, distance):
        return self.move('left', distance)

    def move_right(self, distance):
        return self.move('right', distance)

    def move_up(self, distance):
        return self.move('up', distance)

    def set_speed(self, speed):
        speed = int(round(float(speed) * 27.7778))
        return self.send_command('speed %s' % speed)

    def takeoff(self):
        return self.send_command('takeoff')

    def rotate_cw(self, degrees):
        return self.send_command('cw %s' % degrees)

    def rotate_ccw(self, degrees):
        return self.send_command('ccw %s' % degrees)
