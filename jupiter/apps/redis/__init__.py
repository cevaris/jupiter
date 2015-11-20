from fabric.api import sudo
from fabric.context_managers import cd

from jupiter.apps import App
from jupiter import utils
from jupiter.utils import file


class RedisApp(App):
    version = '3.0.5'
    app_folder = 'redis-{}'.format(version)
    name = '{}.zip'.format(app_folder)
    url = 'https://s3.amazonaws.com/jupiter-apps/{}'.format(name)

    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.app_name = 'redis'
        self.redis_port = self.app_context.get_port('redis_port')

    def install(self):
        sudo('yum install -y gcc-c++')
        self.download_app()
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
