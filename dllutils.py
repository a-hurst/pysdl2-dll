import os
import sys
import subprocess as sub


def find_symlinks(path, names):
    """'ignore' filter for shutil.copytree that identifies whether files are
    symlinks or not. For excluding symlinks when copying .frameworks, since
    they're not needed for pysdl2 and Python wheels don't support them.
    """
    links = []
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        if os.path.islink(filepath):
            links.append(f)
        # Some frameworks have useless duplicates instead of symlinks, so ignore those too
        elif '.framework' in os.path.basename(path) and f != 'Versions':
            links.append(f)
        elif os.path.basename(path) == 'Versions' and f != 'A':
            links.append(f)

    return links


def make_install_lib(src_path, prefix, buildenv, extra_args=None):
    """Builds and installs a library into a given prefix using GNU Make.
    """
    orig_path = os.getcwd()
    os.chdir(src_path)
    success = True

    buildcmds = [
        ['./configure', '--prefix={0}'.format(prefix)],
        ['make'],
        ['make', 'install']
    ]
    for cmd in buildcmds:
        if cmd[0] == './configure' and extra_args:
            cmd = cmd + extra_args
        p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, env=buildenv)
        p.communicate()
        if p.returncode != 0:
            success = False
            break

    os.chdir(orig_path)
    return success
