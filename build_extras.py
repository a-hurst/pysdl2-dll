import os
import sys
import subprocess as sub
import tarfile

from urllib.request import urlopen


FREEDESKTOP_URL = "https://gitlab.freedesktop.org/{0}/{0}/-/archive/"
GITHUB_URL = "https://github.com/{0}/releases/download/"
LIBDIR = "/usr/lib64" if sys.maxsize > 2 ** 32 else "/usr/lib"

extras = {
    'pipewire': {
        'version': "0.3.58",
        'url': FREEDESKTOP_URL.format("pipewire") + "{0}/pipewire-{0}.tar.gz",
        'build_cmds': [
            ['meson', 'setup', 'builddir',
                '-Dprefix=/usr',
                '-Dsession-managers=',
                '-Dspa-plugins=disabled',
                '-Dgstreamer=disabled',
                '-Dpipewire-alsa=disabled',
                '-Dalsa=disabled',
                '-Djack-devel=true',
                '-Dexamples=disabled',
                '-Dtests=disabled',
            ],
            ['meson', 'compile', '-C', 'builddir'],
            ['meson', 'install', '-C', 'builddir'],
        ]
    },
    'libdecor': {
        'version': "0.1.1",
        'url': FREEDESKTOP_URL.format("libdecor") + "{0}/libdecor-{0}.tar.gz",
        'build_cmds': [
            ['meson', 'build', '--buildtype', 'release', '-Dprefix=/usr'],
            ['meson', 'install', '-C', 'build'],
        ]
    },
    'sndio': {
        'version': "1.9.0",
        'url': "https://sndio.org/sndio-{0}.tar.gz",
        'build_cmds': [
            ['./configure', '--prefix=/usr', f'--pkgconfdir={LIBDIR}/pkgconfig'],
            ['make'],
            ['make', 'install'],
            ['ldconfig'],
        ]
    },
    'jack1': {
        'version': "0.126.0",
        'url': GITHUB_URL.format("jackaudio/jack1") + "{0}/jack1-{0}.tar.gz",
        'build_cmds': [
            ['./configure', '--prefix=/usr', f'--libdir={LIBDIR}'],
            ['make'],
            ['make', 'install'],
        ]
    }
}


def fetch_source(liburl, outdir):
    """Downloads and decompresses the source code for a given library.
    """
    # Download tarfile to temporary folder
    srctar = urlopen(liburl)
    srcfile = liburl.split("/")[-1]
    outpath = os.path.join(outdir, srcfile)
    with open(outpath, 'wb') as out:
        out.write(srctar.read())

    # Extract source from archive
    with tarfile.open(outpath, 'r:gz') as z:
        z.extractall(path=outdir)

    return os.path.join(outdir, srcfile.replace(".tar.gz", ""))



# Actually run build script

libname = sys.argv[1]
if not libname in extras.keys():
    e = "build_extras.py is not configured to build the '{0}' library"
    raise RuntimeError(e.format(libname))

libdir = "lib_extra"
if not os.path.exists(libdir):
    os.mkdir(libdir)

# Download and extract source code
info = extras[libname]
sourcedir = fetch_source(info['url'].format(info['version']), libdir)

# Enter source directory and build/install the library
os.chdir(sourcedir)
print("\n=== Building {0} {1} from source ===\n".format(libname, info['version']))
for cmd in info['build_cmds']:
    p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    if p.returncode != 0:
        success = False
        break
