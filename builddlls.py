import os
import sys
import shutil
import tarfile
import subprocess as sub
from zipfile import ZipFile 
from distutils.util import get_platform

try:
    from urllib.request import urlopen # Python 3.x
except ImportError:
    from urllib2 import urlopen # Python 2


libraries = ['SDL2', 'SDL2_image', 'SDL2_ttf', 'SDL2_mixer',  'SDL2_gfx']

libversions = {
    'SDL2': '2.0.14',
    'SDL2_mixer': '2.0.4',
    'SDL2_ttf': '2.0.15',
    'SDL2_image': '2.0.5',
    'SDL2_gfx': '1.0.4'
}

sdl2_urls = {
    'SDL2': 'https://www.libsdl.org/release/SDL2-{0}{1}',
    'SDL2_mixer': 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-{0}{1}',
    'SDL2_ttf': 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-{0}{1}',
    'SDL2_image': 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{0}{1}',
    'SDL2_gfx': 'http://www.ferzkopp.net/Software/SDL2_gfx/SDL2_gfx-{0}{1}'
}


def make_install_lib(src_path, prefix, buildenv, extra_args=None):

    orig_path = os.getcwd()
    os.chdir(src_path)

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
            return False

    os.chdir(orig_path)
    return True


def cmake_install_lib(src_path, prefix, buildenv):

    orig_path = os.getcwd()
    os.chdir(src_path)

    os.mkdir('build')
    os.chdir('build')

    cmake_env = buildenv.copy()
    if 'LD_LIBRARY_PATH' in cmake_env.keys():
        del cmake_env['LD_LIBRARY_PATH']
    print(cmake_env)

    buildcmds = [
        ['cmake',
         '-DBUILD_SHARED_LIBS=ON',
         '-DCMAKE_INSTALL_LIBDIR:PATH={0}'.format(os.path.join(prefix, 'lib')),
         '-DCMAKE_INSTALL_PREFIX:PATH={0}'.format(prefix),
         '..',
        ],
        ['cmake', '--build', '.', '--target', 'install', '--config', 'Release']
    ]
    for cmd in buildcmds:
        p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        p.communicate()
        if p.returncode != 0:
            return False

    os.chdir(orig_path)
    return True


def buildDLLs():

    suffix = '.tar.gz' # source code
    basedir = os.getcwd()
    arch = os.uname()[-1]
    debug = False

    libdir = os.path.join(basedir, 'sdlprefix')
    if os.path.isdir(libdir):
        shutil.rmtree(libdir)
    os.mkdir(libdir)

    # Pre-fetch updated config.guess and config.sub scripts (needed for gfx on ARM & PPC)
    cfgfiles = {}
    cfgnames = ['config.guess', 'config.sub']
    cfgurl = 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f={0};hb=HEAD'
    for name in cfgnames:
        cfgfiles[name] = urlopen(cfgurl.format(name)).read()

    for lib in libraries:

        libversion = libversions[lib]
        print('\n======= Downloading {0} {1} =======\n'.format(lib, libversion))
        
        # Download tar archive containing source
        liburl = sdl2_urls[lib].format(libversion, suffix)
        srctar = urlopen(liburl)
        outpath = os.path.join('temp', lib + suffix)
        with open(outpath, 'wb') as out:
            out.write(srctar.read())
        
        # Extract source from archive
        sourcepath = os.path.join('temp', lib + '-' + libversion)
        with tarfile.open(outpath, 'r:gz') as z:
            z.extractall(path='temp')

        # Set required environment variables for custom prefix
        debug_flags = '-O0 -ggdb3 ' if debug else ''
        buildenv = os.environ.copy()
        pkgconfig_dir = os.path.join(libdir, 'lib', 'pkgconfig')
        builtlib_dir = os.path.join(libdir, 'lib')
        include_dir = os.path.join(libdir, 'include')
        buildenv['PKG_CONFIG_PATH'] = os.path.abspath(pkgconfig_dir)
        buildenv['LD_LIBRARY_PATH'] = os.path.abspath(builtlib_dir)
        buildenv['LDFLAGS'] = "-L" + os.path.abspath(builtlib_dir)
        buildenv['CPPFLAGS'] = debug_flags + '-I{0}'.format(os.path.abspath(include_dir))

        # Update config.guess & config.sub files, if they exist
        for name in cfgnames:
            filepath = os.path.join(sourcepath, name)
            if os.path.exists(filepath):
                os.remove(filepath)
                with open(filepath, 'wb') as out:
                    out.write(cfgfiles[name])

        # Check for any external dependencies and set correct build order
        dependencies = []
        ignore = ['libvorbisidec'] # only needed for special non-standard builds
        build_first = ['zlib', 'harfbuzz']
        build_last = ['libvorbis', 'opusfile', 'flac']
        use_cmake = ['libwebp']
        ext_dir = os.path.join(sourcepath, 'external')
        if os.path.exists(ext_dir):
            dep_dirs = os.listdir(ext_dir)
            deps_first, deps, deps_last = ([], [], [])
            for dep in dep_dirs:
                dep_path = os.path.join(ext_dir, dep)
                if not os.path.isdir(dep_path):
                    continue
                depname, depversion = dep.split('-')
                if depname in ignore:
                    continue
                elif depname in build_first:
                    deps_first.append(dep)
                elif depname in build_last:
                    deps_last.append(dep)
                else:
                    deps.append(dep)
            dependencies = deps_first + deps + deps_last

        # Build any external dependencies
        extra_args = {
            'opusfile': ['--disable-http'],
            'freetype': ['--enable-freetype-config']
        }
        for dep in dependencies:
            depname, depversion = dep.split('-')
            dep_path = os.path.join(ext_dir, dep)
            print('======= Compiling {0} dependency {1} =======\n'.format(lib, dep))
            if depname in use_cmake:
                success = cmake_install_lib(dep_path, libdir, buildenv)
            else:
                xtra_args = None
                if depname in extra_args.keys():
                    xtra_args = extra_args[depname]
                success = make_install_lib(dep_path, libdir, buildenv, xtra_args)
            if not success:
                raise RuntimeError("Error building {0}".format(dep))
            print('\n======= {0} built sucessfully =======\n'.format(dep))

        # Build the library
        print('======= Compiling {0} {1} =======\n'.format(lib, libversion))
        xtra_args = None
        if lib == 'SDL2_gfx' and not arch in ['i386', 'x86_64']:
            xtra_args = '--disable-mmx'
        elif lib == 'SDL2_ttf':
            xtra_args = '--with-ft-prefix={0}'.format(os.path.abspath(libdir))
        success = make_install_lib(dep_path, libdir, buildenv, xtra_args)
        if not success:
                raise RuntimeError("Error building {0}".format(lib))
        print('\n======= {0} {1} built sucessfully =======\n'.format(lib, libversion))
        os.chdir(basedir)

    # Copy compiled binaries to dll folder for bundling in wheel
    for f in os.listdir(os.path.join(libdir, 'lib')):
        if f.split('.')[-1] == "so":
            fpath = os.path.join(libdir, 'lib', f)
            if os.path.islink(fpath):
                fpath = os.path.realpath(fpath)
            libname = os.path.basename(fpath)
            libname_fixed = '.'.join(libname.split('.')[:3])
            lib_outpath = os.path.join(dlldir, libname_fixed)
            shutil.copy(fpath, lib_outpath)
            
    print("Built binaries:")
    print(os.listdir(dlldir))


if __name__ == '__main__':
    #getDLLs(get_platform())
    getDLLs('manylinux2010')
                