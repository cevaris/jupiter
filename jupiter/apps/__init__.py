from collections import OrderedDict

from jupiter import utils


class HostConnection(object):
    def __init__(self, name, port):
        self.name = name
        self.port = port


class AppContext(object):
    def __init__(self, app_slug=None, host_connections=None):
        self.app_slug = app_slug

        if host_connections is None:
            self.host_connections = OrderedDict()
        else:
            self.host_connections = host_connections

    def get_port(self, port_name):
        curr_hostname = utils.hostname()
        connections = self.host_connections.get(curr_hostname)
        port = connections.get(port_name)
        if port:
            return port
        else:
            return None


class App(object):
    """
    :type app_context: AppContext
    """

    def __init__(self, app_context):
        super(App, self).__init__()
        self.app_name = None
        self.app_dir = '/opt/apps'
        self.app_context = app_context
        self.app_slug = self.app_context.app_slug
        self.owners = '{0}:{0}'.format(self.app_slug)
        self.home_dir = '/home/{}'.format(self.app_slug)

    def install(self):
        raise NotImplementedError()

    def post_install(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()
