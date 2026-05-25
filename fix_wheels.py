import os
import glob
import subprocess as sub
from sysconfig import get_platform

override = os.getenv('SDL2DLL_PLATFORM')
platform = get_platform() if not override else override


def find_wheel():
    if os.path.isdir('dist'):
        wheels = glob.glob("dist/pysdl2_dll*.whl")
        if len(wheels):
            return wheels[0]
    return None


def retag_wheel(path, platform, replace=True):
    base_cmd = ['wheel', 'tags']
    if replace:
        base_cmd += ['--remove']
    opts = [
        '--python-tag=py2.py3',
        '--abi-tag=none',
        '--platform-tag=' + platform
    ]
    cmd = base_cmd + opts + [path]
    sub.run(cmd, check=True)


wpath = find_wheel()
if not wpath:
    raise RuntimeError("No wheels found in dist!")

if 'macosx' in platform:
    retag_wheel(wpath, 'macosx_11_0_universal2', replace=False)
    retag_wheel(wpath, 'macosx_10_11_x86_64')
elif platform in ['win32', 'win-amd64']:
    retag_wheel(wpath, platform.replace('-', '_'))
elif 'manylinux' in platform:
    arch = get_platform().split('-')[-1]
    retag_wheel(wpath, '_'.join([platform, arch]))
else:
    retag_wheel(wpath, 'any')
