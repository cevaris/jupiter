import os
import time

from fabric.api import sudo, run, env, warn_only
from fabric.context_managers import cd
from fabric.contrib import files

from jupiter.apps import App


class RabbitMQApp(App):
    version = '3.5.6'
    name = 'rabbitmq-server-generic-unix-{0}.tar.gz'.format(version)
    folder = 'rabbitmq_server-{}'.format(version)
    url = 'https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/{1}'.format(version, name)

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.account_slug = self.app_context.account_slug
        self.rabbitmq_management_port = self.app_context.get_port('rabbitmq_management_port')
        self.rabbitmq_node_port = self.app_context.get_port('rabbitmq_node_port')

        # self.account_slug = 'abc2'
        # self.rabbitmq_node_port = 22002
        # self.rabbitmq_management_port = 22003

    def install(self):
        sudo('yum install -y erlang')

        user_dir = 'rabbitmq/{}'.format(self.account_slug)

        run('mkdir -p {}'.format(user_dir))
        with cd(user_dir):
            run("wget -nc '{}'".format(self.url))
            run('tar xzf {}'.format(self.name))

        self.rabbitmq_config()
        self.rabbitmq_env()

        self.start()
        self.create_user(self.account_slug, '/', 'administrator')
        self.enable_management()
        self.restart()

    def start(self):
        with warn_only():
            with cd(self.rabbitmq_dir()):
                run('sbin/rabbitmq-server -detached', pty=False)
                time.sleep(1)

    def stop(self):
        with warn_only():
            with cd(self.rabbitmq_dir()):
                run('sbin/rabbitmqctl stop')
                time.sleep(1)

    def restart(self):
        self.stop()
        self.start()

    def rabbitmq_dir(self):
        return 'rabbitmq/{}/{}'.format(self.account_slug, self.folder)

    def create_user(self, user, virtual_host, tag='customer'):
        with cd(self.rabbitmq_dir()):
            run('sbin/rabbitmqctl add_user {} pass'.format(user), warn_only=True)
            run('sbin/rabbitmqctl add_vhost {}'.format(virtual_host), warn_only=True)
            run('sbin/rabbitmqctl set_permissions -p {} {} ".*" ".*" ".*"'.format(virtual_host, user))
            run('sbin/rabbitmqctl set_user_tags {} {}'.format(user, tag))
        self.restart()

    def enable_management(self):
        with cd(self.rabbitmq_dir()):
            run('sbin/rabbitmq-plugins enable rabbitmq_management')

    def rabbitmq_config(self):
        context = {
            'rabbitmq_management_port': self.rabbitmq_management_port
        }
        with cd(self.rabbitmq_dir()):
            files.upload_template(
                'rabbitmq.config',
                'etc/rabbitmq/rabbitmq.config',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )

    def rabbitmq_env(self):
        context = {
            'rabbitmq_node_port': self.rabbitmq_node_port,
            'rabbitmq_node_name': self.account_slug,
            'env': env
        }
        with cd(self.rabbitmq_dir()):
            files.upload_template(
                'rabbitmq-env.conf',
                'etc/rabbitmq/rabbitmq-env.conf',
                context=context,
                use_jinja=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates')
            )
