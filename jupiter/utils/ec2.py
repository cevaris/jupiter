import os

from fabric.api import sudo
from fabric.context_managers import cd

from jupiter.utils import file


def create_user(app_slug, sudoer=False):
    sudo('adduser {}'.format(app_slug), warn_only=True)

    home_dir = '/home/{}'.format(app_slug)
    default_owners = '{0}:{0}'.format(app_slug)

    with cd(home_dir):
        file.mkdir('.ssh', owners=default_owners, mode='0700')

        file.upload_template(
            'ssh-authorized-keys.jinja2',
            '.ssh/authorized_keys',
            use_sudo=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
            owners=default_owners,
            mode='0600'
        )

        if sudoer:
            context = {'username': app_slug}
            file.upload_template(
                'etc-sudoers-user.jinja2',
                '/etc/sudoers.d/{}'.format(app_slug),
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                owners='root:root',
                mode='0440'
            )
