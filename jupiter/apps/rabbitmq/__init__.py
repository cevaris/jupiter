import os

import time

from fabric.api import env, sudo, run, warn_only
from fabric.context_managers import cd
from fabric.contrib import files

from jupiter import utils
from jupiter.apps import App


class RabbitMQApp(App):
    version = '3.5.6'
    name = 'rabbitmq-server-generic-unix-{0}.tar.gz'.format(version)
    folder = 'rabbitmq_server-{}'.format(version)
    url = 'https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/{1}'.format(version, name)

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.node_name = "{}-{}".format(self.account_slug, utils.short_hostname())
        self.rabbitmq_management_port = self.app_context.get_port('rabbitmq_management_port')
        self.rabbitmq_node_port = self.app_context.get_port('rabbitmq_node_port')
        self.rabbitmq_dist_port = self.app_context.get_port('rabbitmq_dist_port')

    def install(self):
        self.setup_app_dir()
        sudo('yum install -y erlang')
        self.erlang_cookie_config()

        self.rabbitmq_config()
        self.rabbitmq_env_config()

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
        return '{}/{}/{}/{}'.format(self.app_dir, self.app_context.app_name, self.account_slug, self.folder)

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

    def setup_app_dir(self):
        install_dir = '{}/{}/{}'.format(self.app_dir, self.app_context.app_name, self.account_slug)
        sudo('mkdir -p {}'.format(install_dir))
        sudo('chown {} {}'.format(env.user, install_dir))
        with cd(install_dir):
            run("wget -nc '{}'".format(self.url))
            run('tar xzf {}'.format(self.name))

    def erlang_cookie_config(self):
        cookie = abs(hash('erlang-cookie-{}'.format(self.account_slug)))
        context = {
            'cookie': cookie
        }
        with cd(self.rabbitmq_dir()):
            sudo('touch ~/.erlang.cookie')
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
            run('touch ./etc/rabbitmq/rabbitmq.config')
            files.upload_template(
                'rabbitmq-config.jinja2',
                './etc/rabbitmq/rabbitmq.config',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )

    def rabbitmq_env_config(self):
        context = {
            'rabbitmq_node_port': self.rabbitmq_node_port,
            'rabbitmq_dist_port': self.rabbitmq_dist_port,
            'rabbitmq_node_name': self.node_name,
            'hostname': utils.hostname(),
        }
        with cd(self.rabbitmq_dir()):
            run('touch etc/rabbitmq/rabbitmq-env.conf')
            files.upload_template(
                'rabbitmq-env-conf.jinja2',
                'etc/rabbitmq/rabbitmq-env.conf',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )
