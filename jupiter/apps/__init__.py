from collections import OrderedDict

from enum import Enum

from jupiter import utils


class ClusterNode(Enum):
    No = 0
    Yes = 1


class AppContext(object):
    def __init__(self, app_slug=None, host_connections=None, context=None):
        self.app_slug = app_slug

        if host_connections is None:
            self.host_connections = OrderedDict()
        else:
            self.host_connections = host_connections

        if context is None:
            self.context = OrderedDict()
        else:
            self.context = context

    def get_port(self, port_name):
        curr_hostname = utils.hostname()
        connections = self.host_connections.get(curr_hostname)
        port = connections.get(port_name)
        if port:
            return port
        else:
            return None

    def get(self, key):
        return self.context.get(key)

    def cluster_nodes(self):
        yes_cluster = []
        no_cluster = []
        for hostname, config in self.host_connections.iteritems():
            if config.get('cluster_node') == ClusterNode.Yes:
                yes_cluster.append(hostname)
            if config.get('cluster_node') == ClusterNode.No:
                no_cluster.append(hostname)

        return yes_cluster, no_cluster


class App(object):
    """
    :type app_context: AppContext
    """

    def __init__(self, app_context):
        super(App, self).__init__()
        self.app_name = None
        self.app_root = '/opt/apps'
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
        self.stop()
        self.start()
