import os
import sys
import glob
import tempfile
import subprocess as sub
from zipfile import ZipFile
from sysconfig import get_platform

from getdlls import libraries, libversions, sdl_urls, download


def find_wheel(d):
    if os.path.isdir(d):
        wheels = glob.glob(os.path.join(d, "pysdl3_dll*.whl"))
        if len(wheels):
            return wheels[0]
    return None

def unpack_wheel(path, outdir):
    base_cmd = [sys.executable, '-m', 'wheel', 'unpack']
    sub.run(base_cmd + ['--dest', outdir, path], check=True)
    dirname = os.listdir(outdir)[0]
    return os.path.join(outdir, dirname)

def repack_wheel(wheeldir, outdir):
    base_cmd = [sys.executable, '-m', 'wheel', 'pack']
    sub.run(base_cmd + ['--dest-dir', outdir, wheeldir], check=True)
    if not find_wheel(outdir):
        raise RuntimeError("Failed to repack wheel!")

def add_licenses(wheeldir):
    distdir = os.path.join(wheeldir, os.path.basename(wheeldir) + '.dist-info')
    zipdir = tempfile.mkdtemp(prefix='pysdl3-dll-libs')
    licensedir = os.path.join(distdir, 'licenses', 'libs')
    metadata_path = os.path.join(distdir, 'METADATA')
    new_licenses = []

    # Download and use license files from official Windows x64 binaries
    # NOTE: This assumes bundled binaries are in sync across platforms
    os.mkdir(licensedir)
    for lib in libraries:
        # Download zip archive containing library
        libversion = libversions[lib]
        outpath = os.path.join(zipdir, lib + '.zip')
        download(sdl_urls[lib].format(libversion, '-win32-x64.zip'), outpath)

        # Extract license files from archive
        license_libdir = os.path.join(licensedir, lib)
        os.mkdir(license_libdir)
        with ZipFile(outpath, 'r') as z:
            for name in z.namelist():
                if 'LICENSE' in name or 'README' in name:
                    fname = name.split('/')[-1]
                    new_licenses.append('License-File: libs/' + lib + '/' + fname)
                    outpath = os.path.join(license_libdir, fname)
                    with open(outpath, 'wb') as f:
                        f.write(z.read(name))

    # Update METADATA file with new licences
    with open(metadata_path, 'r') as f:
        metadata = f.read()
    updated = '\n'.join(['License-File: LICENSE'] + new_licenses)
    new_metadata = metadata.replace('License-File: LICENSE', updated)
    with open(metadata_path, 'w') as f:
        f.write(new_metadata)

def retag_wheel(path, platform, replace=True):
    base_cmd = [sys.executable, '-m', 'wheel', 'tags']
    if replace:
        base_cmd += ['--remove']
    opts = [
        '--python-tag=py2.py3',
        '--abi-tag=none',
        '--platform-tag=' + platform
    ]
    cmd = base_cmd + opts + [path]
    sub.run(cmd, check=True)



# Add SDL3 + bundled dynamic library licenses to wheels for distribution

wheelpath = find_wheel('dist')
if not wheelpath:
    raise RuntimeError("No wheels found in dist!")

tmpdir = tempfile.mkdtemp(prefix='pysdl3-dll-wheel')
wheeldir = unpack_wheel(wheelpath, tmpdir)
add_licenses(wheeldir)
os.remove(wheelpath)
repack_wheel(wheeldir, 'dist')


# Update wheel tags to reflect platform-specific binaries

override = os.getenv('SDL3DLL_PLATFORM')
platform = get_platform() if not override else override

if 'macosx' in platform:
    retag_wheel(wheelpath, 'macosx_11_0_universal2', replace=False)
    retag_wheel(wheelpath, 'macosx_10_11_x86_64')
elif platform in ['win32', 'win-amd64']:
    retag_wheel(wheelpath, platform.replace('-', '_'))
elif 'manylinux' in platform:
    arch = get_platform().split('-')[-1]
    retag_wheel(wheelpath, '_'.join([platform, arch]))
else:
    retag_wheel(wheelpath, 'any')
