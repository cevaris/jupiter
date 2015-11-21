import logging

import pytest

logger = logging.getLogger(__file__)


class Config(object):
    hosts = None


def pytest_addoption(parser):
    parser.addoption('--hosts', action='store', default=None, help='integration hosts')


@pytest.fixture
def config(request):
    _config = Config()
    _config.hosts = sorted(list(set(
        filter(lambda x: len(x) > 0,
               map(str.strip, request.config.getoption('--hosts').split(',')))
    )))
    return _config


def test_config(config):
    print config.hosts
