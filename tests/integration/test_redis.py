import pytest
import redis as redislib


@pytest.fixture
def redis(config):
    if not config.hosts:
        raise 'No remote hosts found'
    host_port = config.hosts[0]
    [host, port] = host_port.split(':')
    return redislib.Redis(host=host, port=port)


def test_redis_insert(redis):
    redis.set('test_key', 'test_value')
    assert redis.get('test_key') == 'test_value'
