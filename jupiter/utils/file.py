import re

from fabric.api import sudo, run
from fabric.contrib import files


def upload_template(filename, destination, context=None, use_jinja=True,
                    template_dir=None, use_sudo=False, backup=True, mirror_local_mode=False,
                    mode=None, pty=None, owners=None):
    files.upload_template(
        filename,
        destination,
        context=context,
        use_jinja=use_jinja,
        use_sudo=use_sudo,
        template_dir=template_dir,
        backup=backup,
        mirror_local_mode=mirror_local_mode,
        mode=mode,
        pty=pty
    )
    if owners:
        chown(destination, owners)


def chown(file_path, owners, recursive=False):
    options = []
    if recursive:
        options.append('-R')
    options = ' '.join(options)
    sudo('chown {} {} {}'.format(options, owners, file_path))


def chmod(file_path, mode, recursive=False):
    options = []
    if recursive:
        options.append('-R')
    options = ' '.join(options)
    sudo('chmod {} {} {}'.format(options, mode, file_path))


def update(file_path, mode=None, owners=None, recursive=False):
    if mode:
        chmod(file_path, mode, recursive)

    if owners:
        chown(file_path, owners, recursive)


def wget(url, file_path, mode=None, owners=None):
    if not files.exists(file_path):
        sudo("wget -nc -O {} '{}'".format(file_path, url))
    update(file_path, mode, owners)


def tar_extract(file_path, dest_dir, mode=None, owners=None):
    sudo('tar xzf {}'.format(file_path))
    update(dest_dir, mode, owners, True)


def mkdir(file_path, mode=None, owners=None, recursive=False):
    sudo('mkdir -p {}'.format(file_path))
    update(file_path, mode, owners, recursive)


def touch(file_path, mode=None, owners=None):
    sudo('touch {}'.format(file_path))
    update(file_path, mode, owners)
