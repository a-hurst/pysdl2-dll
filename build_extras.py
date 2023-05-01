import os
import sys
import subprocess as sub
import tarfile

from urllib.request import urlopen


LIBDIR = "/usr/lib64" if sys.maxsize > 2 ** 32 else "/usr/lib"

extras = {
    'sndio': {
        'version': "1.9.0",
        'url': "https://sndio.org/sndio-{0}.tar.gz",
        'build_cmds': [
            ['./configure', '--prefix=/usr', f'--pkgconfdir={LIBDIR}/pkgconfig'],
            ['make'],
            ['make', 'install'],
            ['ldconfig'],
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
