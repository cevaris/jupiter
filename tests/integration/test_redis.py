import pytest
import redis as redislib
from fabric.api import env, settings

from jupiter import app_contexts, apps


@pytest.fixture
def redis():
    app_slug = 'ijk'
    service = 'redis'

    app_context = app_contexts.get(app_slug)
    with settings(
            hosts=app_context.host_connections.keys(),
            host_string=app_context.host_connections.keys()[0]
    ):
        if not env.hosts:
            raise 'No hosts found for {}:{}'.format(service, app_slug)

        apps[service](app_context).start()

        host = env.host_string
        port = app_context.get_port('redis_port')
        return redislib.Redis(host=host, port=port, password='pass')


def test_redis_insert(redis):
    redis.set('test_key', 'test_value')
    assert redis.get('test_key') == 'test_value'
