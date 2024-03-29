import logging
from collections import OrderedDict

from jupiter.apps import AppContext, ClusterNode
from jupiter.apps.rabbitmq import RabbitMQApp
from jupiter.apps.redis import RedisApp

logging.basicConfig()

apps = {
    'rabbitmq': RabbitMQApp,
    'redis': RedisApp
}

app_contexts = {
    'redis,robot': AppContext(
        app_slug='robot',
        host_connections=OrderedDict({
            'ec2-54-209-92-79.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'redis_port': '50000',
            },
        }),
        context={
            'redis_requirepass': 'robot-pass'
        }
    ),
    'rabbitmq,robot': AppContext(
        app_slug='robot',
        host_connections=OrderedDict({
            'ec2-52-91-224-36.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55000',
                'rabbitmq_management_port': '55001',
                'rabbitmq_dist_port': '55002',
            },
            'ec2-54-85-181-200.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55000',
                'rabbitmq_management_port': '55001',
                'rabbitmq_dist_port': '55002',
            },
            'ec2-54-209-92-79.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'rabbitmq_node_port': '55000',
                'rabbitmq_management_port': '55001',
                'rabbitmq_dist_port': '55002',
            }
        }),
        context={
            'rabbitmq_pass': 'pass'
        }
    ),
    'redis,ijk': AppContext(
        app_slug='ijk',
        host_connections=OrderedDict({
            'ec2-54-209-92-79.compute-1.amazonaws.com': {
                'cluster_node': ClusterNode.Yes,
                'redis_port': '55420',
            },
        }),
        context={
            'redis_requirepass': 'pass'
        }
    ),
    'rabbitmq,xyz': AppContext(
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
    'rabbitmq,abc': AppContext(
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
