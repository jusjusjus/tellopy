from socket import socket, AF_INET, SOCK_DGRAM


def get_own_ip():
    dummy_host = ('192.168.10.3', 8888)
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.connect(dummy_host)
        return sock.getsockname()[0]
