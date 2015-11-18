import logging
import os
from collections import OrderedDict

import dotenv

dotenv.read_dotenv()  # NOQA

from fabric.api import env, parallel, sudo
from jupiter.apps import AppContext, ClusterNode
from jupiter.apps.rabbitmq import RabbitMQApp
from jupiter.aws import Ec2

logging.basicConfig()

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')

services = {
    'rabbitmq': RabbitMQApp
}

datastore = {
    'xyz': AppContext(
        app_slug='xyz',
        host_connections=OrderedDict({
            'ec2-52-91-224-36.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55400',
                'rabbitmq_management_port': '55401',
                'rabbitmq_dist_port': '55402',
            },
            'ec2-54-85-181-200.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55400',
                'rabbitmq_management_port': '55401',
                'rabbitmq_dist_port': '55402',
            },
            'ec2-54-209-92-79.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55400',
                'rabbitmq_management_port': '55401',
                'rabbitmq_dist_port': '55402',
            }
        })
    ),
    'abc': AppContext(
        app_slug='abc',
        host_connections=OrderedDict({
            'ec2-52-91-224-36.compute-1.amazonaws.com': {
                'rabbitmq_node_port': '55410',
                'rabbitmq_management_port': '55411',
                'rabbitmq_dist_port': '55412'
            },
            'ec2-54-85-181-200.compute-1.amazonaws.com': {
                'rabbitmq_node_port': '55410',
                'rabbitmq_management_port': '55411',
                'rabbitmq_dist_port': '55412'
            },
            'ec2-54-209-92-79.compute-1.amazonaws.com': {
                'rabbitmq_node_port': '55410',
                'rabbitmq_management_port': '55411',
                'rabbitmq_dist_port': '55412'
            }
        })
    )
}


def aws():
    ec2 = Ec2()
    env.hosts = ec2.instances_dns_names()
    # env.hosts = ['ec2-54-85-181-200.compute-1.amazonaws.com']
    # env.hosts = ['ec2-54-209-92-79.compute-1.amazonaws.com']
    print 'Remote AWS Hosts'
    for host in env.hosts:
        print host


@parallel
def bootstrap():
    app_context = AppContext()

    from jupiter.apps.base import BaseDeployment
    BaseDeployment(app_context).install()

    # May reboot to update hostname, do last
    from jupiter.apps.ec2 import Ec2Package
    Ec2Package(app_context).install()


# @parallel(pool_size=2)
@parallel
def install(service, app_slug):
    from jupiter.utils import ec2
    ec2.create_user(app_slug, sudoer=False)

    app_context = datastore.get(app_slug)
    services[service](app_context).install()


def post_install(service, app_slug):
    app_context = datastore.get(app_slug)
    services[service](app_context).post_install()


@parallel
def start(service, app_slug):
    app_context = datastore.get(app_slug)
    services[service](app_context).start()


@parallel
def restart(service, app_slug):
    app_context = datastore.get(app_slug)
    services[service](app_context).restart()


@parallel
def stop(service, app_slug):
    app_context = datastore.get(app_slug)
    services[service](app_context).stop()


@parallel
def create_system_user():
    env.user = 'ec2-user'
    from jupiter.utils import ec2
    ec2.create_user('system', sudoer=True)


@parallel
def reset_apps():
    sudo('rm -rf /opt/apps/*')
    sudo('killall beam', warn_only=True)
    bootstrap()
