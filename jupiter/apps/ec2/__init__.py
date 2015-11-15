import os

from fabric.api import run, reboot, cd, sudo
from fabric.contrib import files

from jupiter.apps import App


class Ec2Package(App):
    def __init__(self):
        super(Ec2Package, self).__init__()
        self.tools_dir = 'tools'
        run('mkdir -p {}'.format(self.tools_dir))
        self.ec2_metadata = '{}/{}'.format(self.tools_dir, 'ec2-metadata')

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
        with cd(self.tools_dir):
            run('wget http://s3.amazonaws.com/ec2metadata/ec2-metadata')
            sudo('chmod +x ec2-metadata')

        public_dns = run(
            'curl -s http://169.254.169.254/latest/meta-data/public-hostname'
        )
        print 'Found DNS: {}'.format(public_dns)
        return public_dns
