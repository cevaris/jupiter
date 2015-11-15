import hashlib
import os
import time
from fabric.api import sudo, run, env, warn_only
from fabric.context_managers import cd
from fabric.contrib import files
from jupiter.apps import App
from jupiter import utils


class RabbitMQApp(App):
    version = '3.5.6'
    name = 'rabbitmq-server-generic-unix-{0}.tar.gz'.format(version)
    folder = 'rabbitmq_server-{}'.format(version)
    url = 'https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/{1}'.format(version, name)
    salt = 'rmq-salt'

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.node_name = "{}-{}".format(self.account_slug, utils.short_hostname())
        self.rabbitmq_management_port = self.app_context.get_port('rabbitmq_management_port')
        self.rabbitmq_node_port = self.app_context.get_port('rabbitmq_node_port')
        self.rabbitmq_dist_port = self.app_context.get_port('rabbitmq_dist_port')

        # self.account_slug = 'abc2'
        # self.rabbitmq_node_port = 22002
        # self.rabbitmq_management_port = 22003

    def install(self):
        sudo('yum install -y erlang')
        self.erlang_cookie()

        apps_dir = 'rabbitmq/{}'.format(self.account_slug)

        run('mkdir -p {}'.format(apps_dir))
        with cd(apps_dir):
            run("wget -nc '{}'".format(self.url))
            run('tar xzf {}'.format(self.name))

        self.rabbitmq_config()
        self.rabbitmq_env()

        self.start()
        time.sleep(1)
        self.start_app()

        self.create_user(self.account_slug, '/', 'administrator')
        self.enable_management()
        self.restart()

        self.join_cluster()

    def start(self):
        with warn_only():
            with cd(self.rabbitmq_dir()):
                run('sbin/rabbitmq-server -detached', pty=False)
                time.sleep(1)

    def stop(self):
        self.rabbitmqctl('stop', warn_only=True)
        time.sleep(1)

    def restart(self):
        self.stop()
        self.start()

    def rabbitmq_dir(self):
        return 'rabbitmq/{}/{}'.format(self.account_slug, self.folder)

    def rabbitmqctl(self, command, **kwargs):
        with cd(self.rabbitmq_dir()):
            run('sbin/rabbitmqctl {}'.format(command), **kwargs)

    def stop_app(self):
        self.rabbitmqctl('stop_app')

    def start_app(self):
        self.rabbitmqctl('start_app')

    def cluster_status(self):
        self.rabbitmqctl('cluster_status')

    def create_user(self, user, virtual_host, tag='customer'):
        self.rabbitmqctl('add_user {} pass'.format(user), warn_only=True)
        self.rabbitmqctl('add_vhost {}'.format(virtual_host), warn_only=True)
        self.rabbitmqctl('set_permissions -p {} {} ".*" ".*" ".*"'.format(virtual_host, user))
        self.rabbitmqctl('set_user_tags {} {}'.format(user, tag))

    def join_cluster(self):
        self.start()

        self.stop_app()
        self.cluster_status()
        cluster_hosts = self.app_context.host_connections.keys()
        cluster_hosts.remove(utils.hostname())
        cluster_nodes = ['{}-{}@{}'.format(self.account_slug, utils.short_hostname(x), x) for x in cluster_hosts]
        for node in cluster_nodes:
            self.rabbitmqctl('join_cluster {}'.format(node), warn_only=True)
        self.cluster_status()
        self.start_app()

    def enable_management(self):
        with cd(self.rabbitmq_dir()):
            run('sbin/rabbitmq-plugins enable rabbitmq_management')

    def erlang_cookie(self):
        cookie = abs(hash('{}{}'.format(self.salt, self.account_slug)))
        context = {
            'cookie': cookie
        }
        with cd(self.rabbitmq_dir()):
            files.upload_template(
                'erlang-cookie.jinja2',
                '~/.erlang.cookie',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                use_sudo=True,
                backup=False,
                mode='0400'
            )

    def rabbitmq_config(self):
        context = {
            'rabbitmq_management_port': self.rabbitmq_management_port
        }
        with cd(self.rabbitmq_dir()):
            files.upload_template(
                'rabbitmq-config.jinja2',
                'etc/rabbitmq/rabbitmq.config',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )

    def rabbitmq_env(self):
        context = {
            'rabbitmq_node_port': self.rabbitmq_node_port,
            'rabbitmq_dist_port': self.rabbitmq_dist_port,
            'rabbitmq_node_name': self.node_name,
            'hostname': utils.hostname(),
        }
        with cd(self.rabbitmq_dir()):
            files.upload_template(
                'rabbitmq-env-conf.jinja2',
                'etc/rabbitmq/rabbitmq-env.conf',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )
