import os
import time
from fabric.api import sudo
from fabric.context_managers import cd
from jupiter import utils
from jupiter.apps import App
from jupiter.utils import file


class RabbitMQApp(App):
    version = '3.5.6'
    name = 'rabbitmq-server-generic-unix-{0}.tar.gz'.format(version)
    folder = 'rabbitmq_server-{}'.format(version)
    url = 'https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/{1}'.format(version, name)

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.app_name = 'rabbitmq'
        self.rabbitmq_management_port = self.app_context.get_port('rabbitmq_management_port')
        self.rabbitmq_node_port = self.app_context.get_port('rabbitmq_node_port')
        self.rabbitmq_dist_port = self.app_context.get_port('rabbitmq_dist_port')

    def install(self):
        self.download_app()
        sudo('yum install -y erlang')
        self.erlang_cookie_config()

        self.rabbitmq_config()
        self.rabbitmq_env_config()

        self.start()
        time.sleep(1)
        self.start_app()

        self.create_user(self.app_slug, '/', 'administrator')
        self.enable_management()
        self.restart()

    def post_install(self):
        self.join_cluster()

    def start(self):
        with cd(self.rabbitmq_dir()):
            utils.run_as('sbin/rabbitmq-server -detached', self.app_slug, warn_only=True)

        time.sleep(1)

    def stop(self):
        self.rabbitmqctl('stop', warn_only=True)
        time.sleep(1)

    def restart(self):
        self.stop()
        self.start()

    def rabbitmq_dir(self):
        return '{}/{}/{}/{}'.format(self.app_dir, self.app_name, self.app_slug, self.folder)

    def rabbitmqctl(self, command, **kwargs):
        with cd(self.rabbitmq_dir()):
            utils.run_as('sbin/rabbitmqctl {}'.format(command), user=self.app_slug, **kwargs)

    def stop_app(self):
        self.rabbitmqctl('stop_app')

    def start_app(self):
        self.rabbitmqctl('start_app')

    def cluster_status(self):
        self.rabbitmqctl('cluster_status')

    def create_user(self, user, virtual_host, tag='customer'):
        self.rabbitmqctl('add_user {} pass'.format(user), warn_only=True)
        self.rabbitmqctl('add_vhost {}'.format(virtual_host), warn_only=True)
        self.rabbitmqctl("set_permissions -p {} {} '.*' '.*' '.*'".format(virtual_host, user))
        self.rabbitmqctl('set_user_tags {} {}'.format(user, tag))

    def join_cluster(self):
        self.start()
        time.sleep(1)
        self.stop_app()
        self.cluster_status()

        yes_cluster, no_cluster = self.app_context.cluster_nodes()
        hostname = utils.hostname()
        if hostname in no_cluster:
            self.stop_app()
            self.rabbitmqctl('reset')
            self.start_app()
        else:
            cluster_nodes = ['{}@{}'.format(self.app_slug, x) for x in yes_cluster]
            for node in cluster_nodes:
                if hostname not in node:
                    self.rabbitmqctl('join_cluster {}'.format(node), warn_only=True)
            self.start_app()
            if len(yes_cluster) > 2:
                self.rabbitmqctl(
                    'set_policy ha-two "" \'{"ha-mode":"exactly","ha-params":2,"ha-sync-mode":"automatic"}\''
                )
        self.cluster_status()

    def enable_management(self):
        with cd(self.rabbitmq_dir()):
            utils.run_as('sbin/rabbitmq-plugins enable rabbitmq_management', user=self.app_slug)

    def download_app(self):
        install_dir = '{}/{}/{}'.format(self.app_dir, self.app_name, self.app_slug)
        file.mkdir(install_dir, owners=self.owners)
        with cd(install_dir):
            file.wget(self.url, self.name, owners=self.owners)
            file.tar_extract(self.name, self.folder, owners=self.owners)

    def erlang_cookie_config(self):
        cookie = abs(hash('erlang-cookie-{}'.format(self.app_slug)))
        context = {'cookie': cookie}
        cookie_path = '{}/.erlang.cookie'.format(self.home_dir)
        file.touch(cookie_path, mode='0400', owners=self.owners)
        file.upload_template(
            'erlang-cookie.jinja2',
            '{}/.erlang.cookie'.format(self.home_dir),
            context=context,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
            use_sudo=True,
            backup=False,
            mode='0400',
            owners=self.owners
        )

    def rabbitmq_config(self):
        config_path = './etc/rabbitmq/rabbitmq.config'
        context = {
            'rabbitmq_management_port': self.rabbitmq_management_port
        }
        with cd(self.rabbitmq_dir()):
            file.touch(config_path, owners=self.owners)
            file.upload_template(
                'rabbitmq-config.jinja2',
                config_path,
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                owners=self.owners
            )

    def rabbitmq_env_config(self):
        env_path = './etc/rabbitmq/rabbitmq-env.conf'
        context = {
            'rabbitmq_node_port': self.rabbitmq_node_port,
            'rabbitmq_dist_port': self.rabbitmq_dist_port,
            'rabbitmq_node_name': '{}@{}'.format(self.app_slug, utils.hostname()),
            'hostname': utils.hostname(),
        }
        with cd(self.rabbitmq_dir()):
            file.touch(env_path, owners=self.owners)
            file.upload_template(
                'rabbitmq-env-conf.jinja2',
                env_path,
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                owners=self.owners
            )
