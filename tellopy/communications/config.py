
import socket

class Config:
    # '192.168.10.1' for drone operation
    # '127.0.0.1' for testing
    drone_ip: str = '192.168.10.1'
    control_port: int = 8889
    controller_port: int = 8888
    video_port: int = 11111
    # `socket.SOCK_DGRAM` for drone operation
    # `socket.SOCK_STREAM` for testing
    socket_config = socket.SOCK_DGRAM
    # These are response messages
    OK: bytes = b'ok'
    ERROR: bytes = b'error'
    TIMEOUT: bytes = b'timeout'
