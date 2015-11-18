import socket
import uuid

from fabric.api import env, sudo


def next_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def next_slug():
    return str(uuid.uuid4())[9:13]


def hostname():
    host = env.host_string
    if host:
        return host
    else:
        return None


def short_hostname(host=None):
    if not host:
        host = hostname()
    if host and len(host.strip().split('.')) > 0:
        return host.split('.')[0]
    else:
        return None


def run_as(command, user, **kwargs):
    return sudo('su %s -c "%s"' % (user, command), **kwargs)


__all__ = ['ec2', 'files']
