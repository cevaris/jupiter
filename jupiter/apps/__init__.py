class HostConnection(object):
    def __init__(self, hostname, name, port):
        self.name = name
        self.hostname = hostname
        self.port = port


class AppContext(object):
    def __init__(self, account_slug, app_name, host_connections=None):
        self.instances = 1
        self.account_slug = account_slug
        self.app_name = app_name

        if host_connections is None:
            self.host_connections = []
        else:
            self.host_connections = host_connections

    def get_port(self, host_connection_name):
        found = [x.port for x in self.host_connections if x.name == host_connection_name]
        if not found:
            return None
        else:
            return found[0]


class App(object):
    """
    :type app_context: AppContext
    """

    def __init__(self, app_context=None):
        super(App, self).__init__()
        self.app_context = app_context

    def install(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()
