import os
import time

from fabric.api import sudo
from fabric.context_managers import cd

from jupiter import utils
from jupiter.apps import App
from jupiter.utils import file


class RedisApp(App):
    version = '3.0.5'
    app_folder = 'redis-{}'.format(version)
    name = '{}.zip'.format(app_folder)
    url = 'https://s3.amazonaws.com/jupiter-apps/{}'.format(name)

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.app_name = 'redis'
        self.config_path = 'redis.conf'
        self.redis_port = self.app_context.get_port('redis_port')

    def start(self):
        with cd(self.redis_dir()):
            utils.run_as('src/redis-server {}'.format(self.config_path), user=self.app_slug)
        time.sleep(1)

    def stop(self):
        with cd(self.redis_dir()):
            utils.run_as('src/redis-cli -p {} shutdown'.format(self.redis_port), user=self.app_slug)
        time.sleep(1)

    def install(self):
        self.download_app()
        sudo('yum install -y gcc-c++')
        self.redis_conf_file()
        with cd(self.redis_dir()):
            utils.run_as('make', user=self.app_slug)

    def redis_dir(self):
        return '{}/{}/{}'.format(self.app_root, self.app_slug, self.app_folder)

    def download_app(self):
        install_dir = '{}/{}'.format(self.app_root, self.app_slug)
        file.mkdir(install_dir, owners=self.owners)
        with cd(install_dir):
            file.wget(self.url, self.name, owners=self.owners)
            file.unzip(self.name, self.app_folder, owners=self.owners)

    def redis_conf_file(self):
        config_path = 'redis.conf'
        context = {
            'app_slug': self.app_slug,
            'redis_port': self.redis_port
        }
        with cd(self.redis_dir()):
            # file.touch(config_path, owners=self.owners)
            file.upload_template(
                'redis.conf.jinja2',
                self.config_path,
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                owners=self.owners
            )
