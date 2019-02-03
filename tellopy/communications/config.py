
import socket

class Config:
    # '192.168.10.1' for drone operation
    # '127.0.0.1' for testing
    drone_ip = '192.168.10.1'
    control_port = 8889
    controller_port = 8888
    video_port = 11111
    # `socket.SOCK_DGRAM` for drone operation
    # `socket.SOCK_STREAM` for testing
    socket_config = socket.SOCK_DGRAM
    # These are response messages
    OK = b'ok'
    ERROR = b'error'
    TIMEOUT = b'timeout'
