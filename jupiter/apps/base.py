from fabric.api import sudo

from jupiter.apps.deployment import ApplicationDeployment


class EmacsPackage(ApplicationDeployment):
    def install(self):
        sudo('yum install -y emacs-nox')


class LocatePackage(ApplicationDeployment):
    def install(self):
        sudo('yum install -y mlocate')
        sudo('/etc/cron.daily/mlocate.cron')


class BaseDeployment(ApplicationDeployment):
    packages = [
        EmacsPackage,
        LocatePackage
    ]

    def install(self):
        print 'Installing base package'
        map(lambda package: package().install(), self.packages)
