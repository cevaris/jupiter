import pytest
import redis
from fabric.api import env

from jupiter import apps, app_contexts

app_slug = 'ijk'
service = 'redis'

app_context = app_contexts.get(app_slug)
env.hosts = app_context.host_connections.keys(),
env.host_string = app_context.host_connections.keys()[0]
apps[service](app_context).start()


@pytest.fixture
def redis_client():
    host = env.host_string
    port = app_context.get_port('redis_port')
    auth_pass = app_context.get('redis_requirepass')
    return redis.Redis(host=host, port=port, password=auth_pass)


def test_redis_insert(redis_client):
    redis_client.set('test_key', 'test_value')
    assert redis_client.get('test_key') == 'test_value'
