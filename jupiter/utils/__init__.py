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


def hostname_short():
    fqdn = socket.gethostname()
    if fqdn and fqdn.split('.')[0]:
        return fqdn.split('.')[0]
    else:
        return None
