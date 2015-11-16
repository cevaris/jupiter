from fabric.api import sudo, run


def chown(file_path, user_owner=None, group_owner=None):
    if group_owner:
        sudo('chown {}:{} {}'.format(user_owner, group_owner, file_path))
    elif user_owner:
        sudo('chown {} {}'.format(user_owner, file_path))


def chmod(file_path, mode):
    sudo('chmod {} {}'.format(mode, file_path))


def mkdir(file_path, mode=None, user_owner=None, group_owner=None, use_sudo=False):
    if use_sudo:
        sudo('mkdir -p {}'.format(file_path))
    else:
        run('mkdir -p {}'.format(file_path))

    if mode:
        chmod(file_path, mode)

    if user_owner or group_owner:
        chown(file_path, user_owner, group_owner)


def touch(file_path, mode=None, user_owner=None, group_owner=None, use_sudo=False):
    if use_sudo:
        sudo('touch {}'.format(file_path))
    else:
        run('touch {}'.format(file_path))

    if mode:
        chmod(file_path, mode)

    if user_owner or group_owner:
        chown(file_path, user_owner, group_owner)
