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


def chown(file_path, owners):
    sudo('chown {} {}'.format(owners, file_path))


def chmod(file_path, mode):
    sudo('chmod {} {}'.format(mode, file_path))


def mkdir(file_path, mode=None, owners=None, use_sudo=False):
    if use_sudo:
        sudo('mkdir -p {}'.format(file_path))
    else:
        run('mkdir -p {}'.format(file_path))

    if mode:
        chmod(file_path, mode)

    if owners:
        chown(file_path, owners)


def touch(file_path, mode=None, owners=None, use_sudo=False):
    if use_sudo:
        sudo('touch {}'.format(file_path))
    else:
        run('touch {}'.format(file_path))

    if mode:
        chmod(file_path, mode)

    if owners:
        chown(file_path, owners)
