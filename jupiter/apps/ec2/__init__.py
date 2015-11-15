import os

from fabric.api import run, reboot
from fabric.contrib import files

from jupiter.apps import App


class Ec2Package(App):
    def install(self):
        public_dns = self.get_public_dns()
        context = {'public_dns': public_dns}

        files.upload_template(
            'etc-sysconfig-network',
            '/etc/sysconfig/network',
            context=context,
            use_sudo=True,
            use_jinja=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates')
        )

        hostname = run('hostname -f')
        print 'Current hostname[{}]'.format(hostname)
        print 'Requested hostname[{}]'.format(public_dns)

        if hostname.strip() != public_dns.strip():
            print 'Rebooting to update hostname...'
            reboot()

    def get_public_dns(self):
        public_dns = run(
            'curl -s http://169.254.169.254/latest/meta-data/public-hostname'
        )
        print 'Found DNS: {}'.format(public_dns)
        return public_dns
