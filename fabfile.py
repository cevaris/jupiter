import logging
import os
from collections import OrderedDict

import dotenv

dotenv.read_dotenv()  # NOQA

from fabric.api import env, run, local, parallel
from jupiter.apps import AppContext, HostConnection
from jupiter.apps.rabbitmq import RabbitMQApp
from jupiter.aws import Ec2

logging.basicConfig()

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')

services = {
    'rabbitmq': RabbitMQApp
}

datastore = {
    'system': AppContext(
        account_slug='system',
        app_name='system'
    ),
    'xyz': AppContext(
        account_slug='xyz',
        app_name='rabbitmq',
        host_connections=OrderedDict({
            'ec2-52-91-224-36.compute-1.amazonaws.com': [
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55402')
            ],
            'ec2-54-85-181-200.compute-1.amazonaws.com': [
                HostConnection('ec2-54-85-181-200.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-54-85-181-200.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55402')
            ],
            'ec2-54-209-92-79.compute-1.amazonaws.com': [
                HostConnection('ec2-54-209-92-79.compute-1.amazonaws.com', 'rabbitmq_node_port', '55400'),
                HostConnection('ec2-54-209-92-79.compute-1.amazonaws.com', 'rabbitmq_management_port', '55401'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55402')
            ]
        })
    ),
    'abc': AppContext(
        account_slug='abc',
        app_name='rabbitmq',
        host_connections=OrderedDict({
            'ec2-52-91-224-36.compute-1.amazonaws.com': [
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_node_port', '55410'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_management_port', '55411'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55412')
            ],
            'ec2-54-85-181-200.compute-1.amazonaws.com': [
                HostConnection('ec2-54-85-181-200.compute-1.amazonaws.com', 'rabbitmq_node_port', '55410'),
                HostConnection('ec2-54-85-181-200.compute-1.amazonaws.com', 'rabbitmq_management_port', '55411'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55412')
            ],
            'ec2-54-209-92-79.compute-1.amazonaws.com': [
                HostConnection('ec2-54-209-92-79.compute-1.amazonaws.com', 'rabbitmq_node_port', '55410'),
                HostConnection('ec2-54-209-92-79.compute-1.amazonaws.com', 'rabbitmq_management_port', '55411'),
                HostConnection('ec2-52-91-224-36.compute-1.amazonaws.com', 'rabbitmq_dist_port', '55412')
            ]
        })
    )
}


def aws():
    ec2 = Ec2()
    env.hosts = ec2.instances_dns_names()
    # env.hosts = ['ec2-54-85-181-200.compute-1.amazonaws.com']
    # env.hosts = ['ec2-54-209-92-79.compute-1.amazonaws.com']
    # env.hosts = ['ec2-54-209-92-79.compute-1.amazonaws.com']
    print env.hosts
    print 'Remote AWS Hosts'
    for host in env.hosts:
        print host


def local_uname():
    local('uname -a')


def remote_uname():
    run('uname -a')


# @parallel
def bootstrap(account_slug=None):
    print env.hosts
    from jupiter.apps.base import BaseDeployment

    app_context = datastore.get('system')
    BaseDeployment(app_context).install()

    from jupiter.utils.ec2 import Ec2Utils
    if account_slug:
        Ec2Utils.create_user(account_slug, sudoer=False)

    from jupiter.apps.ec2 import Ec2Package
    # May reboot to update hostname, do last
    Ec2Package(app_context).install()


# @parallel(pool_size=2)
# @parallel
def install(service, account_slug):
    app_context = datastore.get(account_slug)
    services[service](app_context).install()


@parallel
def start(service, account_slug):
    app_context = datastore.get(account_slug)
    services[service](app_context).start()


@parallel
def restart(service, account_slug):
    app_context = datastore.get(account_slug)
    services[service](app_context).restart()


@parallel
def stop(service, account_slug):
    app_context = datastore.get(account_slug)
    services[service](app_context).stop()


@parallel
def create_system_user():
    env.user = 'ec2-user'
    from jupiter.utils import ec2
    ec2.create_user('system', sudoer=True)
