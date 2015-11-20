from fabric.api import sudo

from jupiter.apps import App


class EmacsPackage(App):
    def install(self):
        sudo('yum install -y emacs-nox')


class LocatePackage(App):
    def install(self):
        sudo('yum install -y mlocate')
        sudo('/etc/cron.daily/mlocate.cron')


class IPythonPackage(App):
    def install(self):
        sudo('pip install ipython')


class BaseDeployment(App):
    packages = [
        EmacsPackage,
        IPythonPackage,
        LocatePackage,
    ]

    def install(self):
        print 'Installing base package'
        map(lambda package: package(self.app_context).install(), self.packages)

        sudo('mkdir -p {}'.format(self.app_root))
