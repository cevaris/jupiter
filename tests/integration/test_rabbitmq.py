import subprocess
import sys

import pika
import pytest

from jupiter import app_contexts

service = 'rabbitmq'
app_slug = 'robot'
context_key = '{},{}'.format(service, app_slug)


def get_app_context(key):
    return app_contexts.get(key)


def shell(command):
    print 'local exec: {}'.format(' '.join(command))
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(pipe.stdout.readline, ''):
        print(line),
        sys.stdout.flush()
    print 'result: {}'.format(pipe.wait())


@pytest.fixture
def rmq_client(request):
    init = request.config.getoption('--init')
    if init and bool(init):
        shell(['fab', 'all_hosts', 'install:{}'.format(context_key), 'post_install:{}'.format(context_key)])
    else:
        shell(['fab', 'all_hosts', 'start:{}'.format(context_key)])
    app_context = get_app_context(context_key)
    node = app_context.host_connections.keys()[0]
    rabbitmq_node_port = int(app_context.get_port('rabbitmq_node_port', node))
    rabbitmq_pass = app_context.get('rabbitmq_pass')
    creds = pika.credentials.PlainCredentials(app_slug, rabbitmq_pass)
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=node, port=rabbitmq_node_port, credentials=creds
    ))


def test_rabbitmq_insert(rmq_client):
    test_body = 'Hello Worldz!'

    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)
        assert body == test_body
        rmq_client.close()

    channel = rmq_client.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(
        exchange='', routing_key='hello', body=test_body
    )
    print " [x] Sent 'Hello World!'"

    channel.basic_consume(
        callback, queue='hello', no_ack=True
    )
    print ' [*] Waiting for messages. To exit press CTRL+C'
    channel.start_consuming()
