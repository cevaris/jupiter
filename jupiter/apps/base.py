from fabric.api import sudo

from jupiter.apps import App


class EmacsPackage(App):
    def install(self):
        sudo('yum install -y emacs-nox')


class LocatePackage(App):
    def install(self):
        sudo('yum install -y mlocate')
        sudo('/etc/cron.daily/mlocate.cron')


class BaseDeployment(App):
    packages = [
        EmacsPackage,
        LocatePackage
    ]

    def install(self):
        print 'Installing base package'
        map(lambda package: package().install(), self.packages)
