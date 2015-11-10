import socket
import uuid


def next_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def next_slug():
    return str(uuid.uuid4())[9:13]
