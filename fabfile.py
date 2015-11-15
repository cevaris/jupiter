import os
import dotenv  # NOQA

dotenv.read_dotenv()  # NOQA

from fabric.api import env, run, local
from jupiter.apps import AppContext, HostConnection
from jupiter.apps.rabbitmq.package import RabbitMQApp
from jupiter.aws import Ec2
import logging


logging.basicConfig()

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')

services = {
    'rabbitmq': RabbitMQApp
}

host_connections = {
    # 'abc1': AppContext(
    #     'abc1',
    #     'rabbitmq', [
    #         HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_node_port', '22002'),
    #         HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_management_port', '22003')
    #     ]
    # ),
    # '43b2': AppContext(
    #     '43b2',
    #     'rabbitmq', [
    #         HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_node_port', '55490'),
    #         HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_management_port', '55489')
    #     ]
    # ),
    'xyz': AppContext(
        account_slug='xyz',
        app_name='rabbitmq',
        host_connections=[
            [
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401')
            ],
            [
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401')
            ],
            [
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-54-85-52-212.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401')
            ]
        ]
    )
}


def aws():
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

    from jupiter.apps.ec2 import Ec2Package
    # May reboot to update hostname, do last
    Ec2Package().install()


def install(service, account_slug):
    app_context = host_connections.get(account_slug)
    services[service](app_context).install()

# def start(service, account_slug):
#     services[service](account_slug).start()
#
#
# def stop(service, account_slug):
#     services[service](account_slug).stop()
#
#
# def restart(service, account_slug):
#     services[service](account_slug).restart()
