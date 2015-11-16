import os
from fabric.api import sudo
from fabric.context_managers import cd
# from fabric.contrib import files

from jupiter.utils import shell
from jupiter.utils import file


def create_user(account_slug, sudoer=False):
    sudo('adduser {}'.format(account_slug), warn_only=True)

    home_dir = '/home/{}'.format(account_slug)

    with cd(home_dir):
        shell.mkdir('.ssh', user_owner=account_slug, group_owner=account_slug, mode='0700', use_sudo=True)

        file.upload_template(
            'ssh-authorized-keys.jinja2',
            '.ssh/authorized_keys',
            use_sudo=True,
            template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
            user_owner=account_slug,
            group_owner=account_slug,
            mode='0600'
        )

        if sudoer:
            sudoers_file = '/etc/sudoers.d/{}'.format(account_slug)
            context = {'username': account_slug}
            file.upload_template(
                'etc-sudoers-user.jinja2',
                sudoers_file,
                context=context,
                use_sudo=True,
                template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
                user_owner='root',
                group_owner='root',
                mode='0440',
            )
