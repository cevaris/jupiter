import os

import dotenv
import pytest

dotenv.read_dotenv()  # NOQA

from fabric.api import env

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')


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
