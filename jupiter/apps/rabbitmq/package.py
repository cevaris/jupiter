import os
import time

from fabric.api import sudo, run, env, warn_only
from fabric.context_managers import cd
from fabric.contrib import files

from jupiter.apps.deployment import ApplicationDeployment


class RabbitMQDeployment(ApplicationDeployment):
    version = '3.5.6'
    name = 'rabbitmq-server-generic-unix-{0}.tar.gz'.format(version)
    folder = 'rabbitmq_server-{}'.format(version)
    url = 'https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/{1}'.format(version, name)

    def install(self):
        sudo('yum install -y erlang')

        user_dir = 'rabbitmq/{}'.format(self.user_slug)

        run('mkdir -p {}'.format(user_dir))
        with cd(user_dir):
            run("wget -nc '{}'".format(self.url))
            run('tar xvzf {}'.format(self.name))

            with cd(self.folder):
                self.rabbitmq_config()
                self.rabbitmq_env()

    def start(self):
        rabbitmq_dir = 'rabbitmq/{}/{}'.format(self.user_slug, self.folder)
        with warn_only():
            with cd(rabbitmq_dir):
                run('sbin/rabbitmq-server -detached', pty=False)

    def stop(self):
        rabbitmq_dir = 'rabbitmq/{}/{}'.format(self.user_slug, self.folder)
        with warn_only():
            with cd(rabbitmq_dir):
                run('sbin/rabbitmqctl stop')

    def restart(self):
        self.stop()
        time.sleep(2)
        self.start()

    def rabbitmq_config(self):
        context = {
            'rabbitmq_management_port': 20021
        }
        files.upload_template(
            'rabbitmq.config',
            'etc/rabbitmq/rabbitmq.config',
            context=context,
            use_jinja=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates')
        )

    def rabbitmq_env(self):
        context = {
            'rabbitmq_node_port': 20020,
            'rabbitmq_node_name': self.user_slug,
            'env': env
        }
        files.upload_template(
            'rabbitmq-env.conf',
            'etc/rabbitmq/rabbitmq-env.conf',
            context=context,
            use_jinja=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates')
        )
