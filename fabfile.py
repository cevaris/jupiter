import os

import dotenv  # NOQA

dotenv.read_dotenv()  # NOQA

from fabric.api import env, run, local
from jupiter.apps.rabbitmq.package import RabbitMQDeployment
from jupiter.aws import Ec2

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')

services = {
    'rabbitmq': RabbitMQDeployment
}


def staging():
    ec2 = Ec2()
    env.hosts = ec2.instances_dns_names()
    print env


def local_uname():
    local('uname -a')


def remote_uname():
    run('uname -a')


def bootstrap():
    from jupiter.apps.base import BaseDeployment
    job = BaseDeployment()
    job.install()


def rabbitmq():
    job = services['rabbitmq']
    job.install()


def start(service):
    services[service]().start()


def stop(service):
    services[service]().stop()


def restart(service):
    services[service]().restart()
