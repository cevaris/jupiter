import os

from fabric.api import run, reboot, cd, sudo
from fabric.contrib import files

from jupiter.apps import App


class Ec2Package(App):
    def __init__(self, app_context):
        App.__init__(self, app_context)
        self.tools_dir = 'tools'
        self.ec2_metadata = '{}/{}'.format(self.tools_dir, 'ec2-metadata')
        self.install_tools()

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

    def install_tools(self):
        run('mkdir -p {}'.format(self.tools_dir))
        with cd(self.tools_dir):
            run('wget -nc http://s3.amazonaws.com/ec2metadata/ec2-metadata')
            sudo('chmod +x ec2-metadata')

    def get_public_dns(self):
        public_dns = run(
            'curl -s http://instance-data/latest/meta-data/public-hostname'
        )
        print 'Found DNS: {}'.format(public_dns)
        return public_dns
