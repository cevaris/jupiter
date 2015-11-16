from fabric.contrib import files
from jupiter.utils import shell


def upload_template(filename, destination, context=None, use_jinja=True,
                    template_dir=None, use_sudo=False, backup=True, mirror_local_mode=False,
                    mode=None, pty=None, user_owner=None, group_owner=None):
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
    if user_owner or group_owner:
        shell.chown(destination, user_owner=user_owner, group_owner=group_owner)
