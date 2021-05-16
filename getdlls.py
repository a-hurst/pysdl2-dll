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


libraries = ['SDL2', 'SDL2_mixer', 'SDL2_ttf', 'SDL2_image', 'SDL2_gfx']

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
    'SDL2_gfx': 'https://github.com/a-hurst/sdl2gfx-builds/releases/download/{0}/SDL2_gfx-{0}{1}'
}


def getDLLs(platform_name):
    
    dlldir = os.path.join('sdl2dll', 'dll')
    licensedir = os.path.join('sdl_licenses')
    for d in ['temp', 'build', dlldir, licensedir]:
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.mkdir(d)

    # Generate license disclaimer for SDL2 libraries (all under zlib)
    sdl_licensepath = os.path.join(licensedir, 'LICENSE.SDL2.txt')
    with open(sdl_licensepath, 'w') as l:
        l.write("SDL2 License Info\n---\n\n")
        l.write("SDL2, SDL2_mixer, SDL2_ttf, SDL2_image, and SDL2_gfx are all distributed\n")
        l.write("under the terms of the zlib license: http://www.zlib.net/zlib_license.html\n")
    
    if 'macosx' in platform_name:
        
        for lib in libraries:
            
            mountpoint = '/tmp/' + lib
            dllname = lib + '.framework'
            dllpath = os.path.join(mountpoint, dllname)
            dlloutpath = os.path.join(dlldir, dllname)
            
            # Download disk image containing library
            libversion = libversions[lib]
            dmg = urlopen(sdl2_urls[lib].format(libversion, '.dmg'))
            outpath = os.path.join('temp', lib + '.dmg')
            with open(outpath, 'wb') as out:
                out.write(dmg.read())
            
            # Mount image, extract framework, then unmount
            sub.check_call(['hdiutil', 'attach', outpath, '-mountpoint', mountpoint])
            shutil.copytree(dllpath, dlloutpath, symlinks=True, ignore=find_symlinks)
            sub.call(['hdiutil', 'unmount', mountpoint])

            # Extract license info from frameworks bundled within main framework
            extraframeworkpath = os.path.join(dlloutpath, 'Versions', 'A', 'Frameworks')
            if os.path.exists(extraframeworkpath):
                for f in os.listdir(extraframeworkpath):
                    resourcepath = os.path.join(extraframeworkpath, f, 'Versions', 'A', 'Resources')
                    if os.path.exists(resourcepath):
                        for name in os.listdir(resourcepath):
                            if 'LICENSE' in name:
                                licensepath = os.path.join(resourcepath, name)
                                outpath = os.path.join(licensedir, name)
                                shutil.copyfile(licensepath, outpath)

    elif platform_name in ['win32', 'win-amd64']:
        
        suffix = '-win32-x64.zip' if platform_name == 'win-amd64' else '-win32-x86.zip'
        
        for lib in libraries:
            
            # Download zip archive containing library
            libversion = libversions[lib]
            dllzip = urlopen(sdl2_urls[lib].format(libversion, suffix))
            outpath = os.path.join('temp', lib + '.zip')
            with open(outpath, 'wb') as out:
                out.write(dllzip.read())
            
            # Extract dlls and license files from archive
            with ZipFile(outpath, 'r') as z:
                for name in z.namelist():
                    if name[-4:] == '.dll':
                        z.extract(name, dlldir)
                    elif 'LICENSE' in name:
                        z.extract(name, licensedir)

    elif 'manylinux' in platform_name or os.getenv('SDL2DLL_UNIX_COMPILE', '0') == '1':

        # Create custom prefix in which to install the SDL2 libs + dependencies
        basedir = os.getcwd()
        libdir = os.path.join(basedir, 'sdlprefix')
        if os.path.isdir(libdir):
            shutil.rmtree(libdir)
        os.mkdir(libdir)

        # Build and install everything into the custom prefix
        sdl2_urls['SDL2_gfx'] = 'http://www.ferzkopp.net/Software/SDL2_gfx/SDL2_gfx-{0}{1}'
        buildDLLs(libraries, basedir, libdir)

        # Copy all compiled binaries to dll folder for bundling in wheel
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

    else:

        # Create dummy file indicating that SDL2 binaries are not available on this platform
        dummyfile = os.path.join(dlldir, '.unsupported')
        with open(dummyfile, 'w') as f:
            f.write("No dlls available for this platform!")

        # Remove unneeded license file
        os.remove(sdl_licensepath)

    shutil.rmtree('temp')


def buildDLLs(libraries, basedir, libdir):

        suffix = '.tar.gz' # source code

        # Set required environment variables for custom prefix
        buildenv = os.environ.copy()
        pkgconfig_dir = os.path.join(libdir, 'lib', 'pkgconfig')
        builtlib_dir = os.path.join(libdir, 'lib')
        include_dir = os.path.join(libdir, 'include')
        buildenv['PKG_CONFIG_PATH'] = os.path.abspath(pkgconfig_dir)
        buildenv['LD_LIBRARY_PATH'] = os.path.abspath(builtlib_dir)
        buildenv['LDFLAGS'] = "-L" + os.path.abspath(builtlib_dir)
        buildenv['CPPFLAGS'] = '-I{0}'.format(os.path.abspath(include_dir))

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

            # Check for any external dependencies and set correct build order
            dependencies = []
            ignore = [
                'libvorbisidec', # only needed for special non-standard builds
                'libwebp' # currently breaks build process, some libtool issue?
            ] 
            build_first = ['zlib', 'harfbuzz']
            build_last = ['libvorbis', 'opusfile', 'flac']
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
            if lib == 'SDL2_ttf':
                xtra_args = ['--with-ft-prefix={0}'.format(os.path.abspath(libdir))]
            success = make_install_lib(sourcepath, libdir, buildenv, xtra_args)
            if not success:
                raise RuntimeError("Error building {0}".format(lib))
            print('\n======= {0} {1} built sucessfully =======\n'.format(lib, libversion))
            os.chdir(basedir)



# Helper functions for facilitating the compiling and/or bundling of binaries

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


if __name__ == '__main__':
    getDLLs(get_platform())
                