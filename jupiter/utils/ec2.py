import os
from fabric.api import sudo
from fabric.context_managers import cd

from jupiter.utils import file


def create_user(account_slug, sudoer=False):
    sudo('adduser {}'.format(account_slug), warn_only=True)

    home_dir = '/home/{}'.format(account_slug)
    default_owners = '{0}:{0}'.format(account_slug)

    with cd(home_dir):
        file.mkdir('.ssh', owners=default_owners, mode='0700', use_sudo=True)

        file.upload_template(
            'ssh-authorized-keys.jinja2',
            '.ssh/authorized_keys',
            use_sudo=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
            owners=default_owners,
            mode='0600'
        )

        if sudoer:
            context = {'username': account_slug}
            file.upload_template(
                'etc-sudoers-user.jinja2',
                '/etc/sudoers.d/{}'.format(account_slug),
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                owners='root:root',
                mode='0440'
            )
