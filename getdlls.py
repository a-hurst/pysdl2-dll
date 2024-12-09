import os
import sys
import time
import shutil
import tarfile
import subprocess as sub
from zipfile import ZipFile
from distutils.util import get_platform

try:
    import urllib.request
    from urllib.request import urlopen # Python 3.x
except ImportError:
    from urllib2 import urlopen # Python 2


libraries = ['SDL2', 'SDL2_mixer', 'SDL2_ttf', 'SDL2_image', 'SDL2_gfx']

libversions = {
    'SDL2': '2.30.10',
    'SDL2_mixer': '2.8.0',
    'SDL2_ttf': '2.22.0',
    'SDL2_image': '2.8.2',
    'SDL2_gfx': '1.0.4'
}

url_fmt = 'https://github.com/libsdl-org/SDL{LIB}/releases/download/release-{0}/SDL2{LIB}-{0}{1}'
url_fmt_pre = url_fmt.replace('release-', 'prerelease-')
sdl2_urls = {
    'SDL2': url_fmt.replace('{LIB}', ''),
    'SDL2_mixer': url_fmt.replace('{LIB}', '_mixer'),
    'SDL2_ttf': url_fmt.replace('{LIB}', '_ttf'),
    'SDL2_image': url_fmt.replace('{LIB}', '_image'),
    'SDL2_gfx': 'https://github.com/a-hurst/sdl2gfx-builds/releases/download/{0}/SDL2_gfx-{0}{1}'
}

cmake_opts = {
    #'SDL2': {
    #    'SDL_SSE2': 'ON',
    #    'SDL_ARMNEON': 'ON',
    #},
    'SDL2_mixer': {
        'SDL2MIXER_VENDORED': 'ON',
        'SDL2MIXER_GME': 'ON',
        'SDL2MIXER_FLAC_LIBFLAC': 'OFF', # Match macOS and Windows binaries, which use dr_flac
    },
    'SDL2_ttf': {
        'SDL2TTF_VENDORED': 'ON',
        'SDL2TTF_HARFBUZZ': 'ON',
    },
    'SDL2_image': {
        'SDL2IMAGE_VENDORED': 'ON',
        'SDL2IMAGE_TIF': 'ON',
        'SDL2IMAGE_WEBP': 'ON',
        'SDL2IMAGE_AVIF': 'ON',
        'DAV1D_WITH_AVX': 'OFF',
    }
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
            optpath = os.path.join(mountpoint, 'optional')
            extraframeworkpath = os.path.join(dlloutpath, 'Versions', 'A', 'Frameworks')
            
            # Download disk image containing library
            outpath = os.path.join('temp', lib + '.dmg')
            libversion = libversions[lib]
            download(sdl2_urls[lib].format(libversion, '.dmg'), outpath)
            
            # Mount image, extract framework (and any optional frameworks), then unmount
            sub.check_call(['hdiutil', 'attach', outpath, '-mountpoint', mountpoint])
            shutil.copytree(dllpath, dlloutpath, symlinks=True, ignore=find_symlinks)
            if os.path.isdir(optpath):
                shutil.copytree(
                    optpath, extraframeworkpath, symlinks=True, ignore=find_symlinks
                )
            sub.call(['hdiutil', 'unmount', mountpoint])

            # Extract license info from frameworks bundled within main framework
            if os.path.exists(extraframeworkpath):
                for f in os.listdir(extraframeworkpath):
                    resourcepath = os.path.join(extraframeworkpath, f, 'Versions', 'A', 'Resources')
                    if os.path.exists(resourcepath):
                        for name in os.listdir(resourcepath):
                            if 'LICENSE' in name:
                                licensepath = os.path.join(resourcepath, name)
                                outpath = os.path.join(licensedir, name)
                                shutil.copyfile(licensepath, outpath)

            # Extract license info for statically-linked libraries
            resourcepath = os.path.join(dlloutpath, 'Versions', 'A', 'Resources')
            for name in os.listdir(resourcepath):
                if 'LICENSE' in name or name == "FTL.TXT":
                    licensepath = os.path.join(resourcepath, name)
                    outpath = os.path.join(licensedir, name)
                    shutil.copyfile(licensepath, outpath)

    elif platform_name in ['win32', 'win-amd64']:
        
        suffix = '-win32-x64.zip' if platform_name == 'win-amd64' else '-win32-x86.zip'
        
        for lib in libraries:
            
            # Download zip archive containing library
            libversion = libversions[lib]
            outpath = os.path.join('temp', lib + '.zip')
            download(sdl2_urls[lib].format(libversion, suffix), outpath)
            
            # Extract dlls and license files from archive
            with ZipFile(outpath, 'r') as z:
                for name in z.namelist():
                    if name[-4:] == '.dll':
                        z.extract(name, dlldir)
                    elif 'LICENSE' in name:
                        z.extract(name, licensedir)

            # Move any optional dlls and licenses into their respective root folders
            for d in [dlldir, licensedir]:
                optdir = os.path.join(d, 'optional')
                if os.path.isdir(optdir):
                    for f in os.listdir(optdir):
                        shutil.move(os.path.join(optdir, f), os.path.join(d, f))

    elif 'manylinux' in platform_name or os.getenv('SDL2DLL_UNIX_COMPILE', '0') == '1':

        # Create custom prefix in which to install the SDL2 libs + dependencies
        basedir = os.getcwd()
        libdir = os.path.join(basedir, 'sdlprefix')
        if os.path.isdir(libdir):
            shutil.rmtree(libdir)
        os.mkdir(libdir)

        # Download and use license files from official Windows binaries
        for lib in libraries:
            # Download zip archive containing library
            libversion = libversions[lib]
            outpath = os.path.join('temp', lib + '.zip')
            download(sdl2_urls[lib].format(libversion, '-win32-x64.zip'), outpath)

            # Extract license files from archive
            with ZipFile(outpath, 'r') as z:
                for name in z.namelist():
                    if 'LICENSE' in name:
                        z.extract(name, licensedir)

            # Move any optional licenses into the root license folder
            optdir = os.path.join(licensedir, 'optional')
            if os.path.isdir(optdir):
                for f in os.listdir(optdir):
                    shutil.move(os.path.join(optdir, f), os.path.join(licensedir, f))

        # Build and install everything into the custom prefix
        sdl2_urls['SDL2_gfx'] = 'http://www.ferzkopp.net/Software/SDL2_gfx/SDL2_gfx-{0}{1}'
        buildDLLs(libraries, basedir, libdir)

        # Copy all compiled binaries to dll folder for bundling in wheel
        for f in os.listdir(os.path.join(libdir, 'lib')):
            fpath = os.path.join(libdir, 'lib', f)
            if f.split('.')[-1] == "so":
                if os.path.islink(fpath):
                    fpath = os.path.realpath(fpath)
                libname = os.path.basename(fpath)
                libname_base = libname.split('.')[0]
                if libname_base == 'libwebpdemux':
                    # Work around linking issues with libwebpdemux
                    libname = 'libwebpdemux.so.2.6.0'
                    rename_dependency(fpath, 'libwebp.so.7.5.0', 'libwebp.so.1.0.3')
                elif libname_base == 'libtiff':
                    # Work around linking issues with libtiff
                    libname = 'libtiff.so.5'
                elif libname_base in ['libwebp']:
                    # No clue why this is an exception to the below rule
                    libname = libname
                else:
                    # SDL dynamic linking code usually expects truncated .so names
                    libname = '.'.join(libname.split('.')[:3])
                lib_outpath = os.path.join(dlldir, libname)
                shutil.copy(fpath, lib_outpath)

        # Update library runpaths to allow loading from within sdl2dll folder
        set_relative_runpaths(dlldir)

        # If release, strip debug symbols from the binaries to reduce file size
        if int(os.getenv("SDL2DLL_RELEASE", 0)) == 1:
            success = strip_debug_symbols(dlldir)
            if success:
                print("*** Successfully stripped debug symbols from binaries ***\n")
            else:
                print("*** NOTE: Failed to strip debug symbols from binaries ***\n")

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
        arch = os.uname()[-1]

        # Set required environment variables for custom prefix
        buildenv = os.environ.copy()
        pkgconfig_dir = os.path.join(libdir, 'lib', 'pkgconfig')
        builtlib_dir = os.path.join(libdir, 'lib')
        include_dir = os.path.join(libdir, 'include')
        buildenv['PKG_CONFIG_PATH'] = os.path.abspath(pkgconfig_dir)
        buildenv['LD_LIBRARY_PATH'] = os.path.abspath(builtlib_dir)
        buildenv['LDFLAGS'] = "-L" + os.path.abspath(builtlib_dir)
        buildenv['CPPFLAGS'] = '-I{0}'.format(os.path.abspath(include_dir))

        # Fetch updated config.guess/config.sub scripts (needed for gfx on non-x86)
        cfgfiles = {}
        cfgnames = ['config.guess', 'config.sub']
        cfgurl = 'https://git.savannah.gnu.org/cgit/config.git/plain/{0}'
        for name in cfgnames:
            cfgfiles[name] = urlopen(cfgurl.format(name)).read()

        # Disable dav1d ASM on manylinux2014 since nasm version is too old
        if os.getenv("AUDITWHEEL_POLICY", "") == "manylinux2014":
            cmake_opts["SDL2_image"]["DAV1D_ASM"] = "OFF"

        for lib in libraries:

            libversion = libversions[lib]
            print('\n======= Downloading {0} {1} =======\n'.format(lib, libversion))

            # Download and extract tar archive containing source
            liburl = sdl2_urls[lib].format(libversion, suffix)
            libfolder = lib + '-' + libversion
            sourcepath = fetch_source(libfolder, liburl, outdir='temp')

            # Check for and download any external dependencies
            ext_dir = os.path.join(sourcepath, 'external')
            download_sh = os.path.join(ext_dir, 'download.sh')
            if os.path.exists(download_sh) and not lib == "SDL2_ttf":
                # NOTE: As of 2.22.0, ttf includes external sources in .tar.gz
                print('======= Downloading optional libraries for {0} =======\n'.format(lib))
                download_external(ext_dir)
                print('')

            # Apply any patches to the source if necessary
            if lib == 'SDL2_image':
                # Ensure libwebp isn't compiled with mandatory SSE4.1 support
                cpu_cmake = os.path.join(ext_dir, 'libwebp', 'cmake', 'cpu.cmake')
                old = 'NOT ENABLE_SIMD'
                new = 'WEBP_SIMD_FLAG STREQUAL "SSE41" OR NOT ENABLE_SIMD'
                patch_file(cpu_cmake, old, new)

            # Build library and its dependencies
            print('======= Compiling {0} {1} =======\n'.format(lib, libversion))
            if lib in cmake_opts.keys():
                # Build using CMake
                opts = cmake_opts[lib]
                success = cmake_install_lib(sourcepath, libdir, buildenv, opts)
            else:
                # Build using autotools
                xtra_args = None
                if lib == 'SDL2':
                    xtra_args = ['--enable-libudev=no']
                elif lib == 'SDL2_gfx' and not arch in ['i686', 'x86_64']:
                    xtra_args = ['--disable-mmx']
                success = make_install_lib(sourcepath, libdir, buildenv, xtra_args, cfgfiles)

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


def fetch_source(libfolder, liburl, outdir):
    """Downloads and decompresses the source code for a given library.
    """
    # Download tarfile to temporary folder
    outpath = os.path.join(outdir, libfolder + '.tar.gz')
    download(liburl, outpath)

    # Extract source from archive
    with tarfile.open(outpath, 'r:gz') as z:
        z.extractall(path=outdir)

    return os.path.join(outdir, libfolder)


def download(url, outpath):
    """Downloads a file from a URL to a given path.
    """
    attempts = 0
    while attempts < 3:
        try:
            data = urlopen(url)
            break
        except OSError:
            time.sleep(0.2)
            attempts += 1

    with open(outpath, 'wb') as out:
        out.write(data.read())


def download_external(ext_path):
    """Downloads the available optional dependencies for a library.
    """
    orig_path = os.getcwd()
    os.chdir(ext_path)
    
    p = sub.Popen("./download.sh", stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    if p.returncode != 0:
        raise RuntimeError("Unable to download external libraries.")

    os.chdir(orig_path)


def make_install_lib(src_path, prefix, buildenv, extra_args=None, config={}):
    """Builds and installs a library into a given prefix using GNU Make.
    """
    orig_path = os.getcwd()
    os.chdir(src_path)
    success = True

    # If updated config.guess/config.sub files provided, use those
    for name in config.keys():
        subdir_path = os.path.join('config', name)
        filepath = subdir_path if os.path.isfile(subdir_path) else name
        with open(filepath, 'wb') as out:
            out.write(config[name])

    buildcmds = [
        ['./configure', '--prefix={0}'.format(prefix)],
        ['make', '-j2'],
        ['make', 'install']
    ]
    if not os.path.exists("configure"):
        buildcmds = ['./autogen.sh'] + buildcmds
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


def build_cmake_opts(optdict):
    """Generates a list of CMake options from a Python dict.
    """
    opts = []
    tmp = "-D{0}={1}"
    for arg, value in optdict.items():
        opt = tmp.format(arg, value)
        opts.append(opt)

    return opts


def cmake_install_lib(src_path, prefix, buildenv, opts=None):
    """Builds and installs a library into a given prefix using CMake.
    """
    orig_path = os.getcwd()
    os.chdir(src_path)
    success = True

    # Create a build directory and switch to it
    os.mkdir('build')
    os.chdir('build')

    # Initialize CMake options
    if not opts:
        opts = {}
    opts['CMAKE_INSTALL_PREFIX'] = prefix
    opts['CMAKE_INSTALL_LIBDIR'] = 'lib'
    opts['CMAKE_INSTALL_RPATH'] = prefix
    if int(os.getenv("SDL2DLL_RELEASE", 0)) == 1:
        opts['CMAKE_BUILD_TYPE'] = 'Release'
    else:
        opts['CMAKE_BUILD_TYPE'] = 'Debug'

    buildcmds = [
        ['cmake', '..'] + build_cmake_opts(opts),
        ['make', '-j2'],
        ['make', 'install']
    ]
    for cmd in buildcmds:
        p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, env=buildenv)
        p.communicate()
        if p.returncode != 0:
            success = False
            break

    os.chdir(orig_path)
    return success


def set_relative_runpaths(libdir):
    """Fixes the runpaths of all .so files in a folder to be relative to their
    own location, such that libraries will be able to find and load their
    dependencies if they exist the same folder.
    """
    libs = [f for f in os.listdir(libdir) if '.so' in f]
    orig_path = os.getcwd()
    os.chdir(libdir)
    success = True

    cmd = ['patchelf', '--set-rpath', '$ORIGIN']
    for lib in libs:
        p = sub.Popen(cmd + [lib], stdout=sys.stdout, stderr=sys.stderr)
        p.communicate()
        if p.returncode != 0:
            success = False
            break

    os.chdir(orig_path)
    return success


def rename_dependency(libpath, depname, newname):
    """Renames a dependency in a given dynamic library.
    """
    cmd = ['patchelf', '--replace-needed', depname, newname, libpath]
    p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    return p.returncode == 0


def rename_library(libdir, name, newname, fix_links):
    """Renames a library to avoid name collisions, patching other libraries
    that depend on it accordingly.
    """
    libs = [f for f in os.listdir(libdir) if '.so' in f]
    orig_path = os.getcwd()
    os.chdir(libdir)
    success = True

    # Rename the library
    libname = [f for f in libs if name in f][0]
    libname_new = libname.replace(name, newname)
    os.rename(libname, libname_new)

    # Update names in any libraries that link to the renamed one
    to_patch = [f for f in libs if f.split('.')[0] in fix_links]
    for lib in to_patch:
        success = rename_dependency(lib, libname, libname_new)
        if not success:
            break

    os.chdir(orig_path)
    return success


def strip_debug_symbols(libdir):
    """Strips the debug symbols from a folder of compiled binaries to reduce
    file size.
    """
    libs = [f for f in os.listdir(libdir) if '.so' in f]
    success = True

    # Strip debug symbols from each compiled library
    for lib in libs:
        libpath = os.path.join(libdir, lib)
        cmd = ['strip', '--strip-debug', libpath]
        p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        p.communicate()
        if p.returncode != 0:
            success = False
            break

    return success


def patch_file(fpath, find, replace):
    """Finds and replaces a given string in a file.
    """
    with open(fpath, 'r') as f:
        content = f.read()
    with open(fpath, 'w') as f:
        f.write(content.replace(find, replace))


if __name__ == '__main__':
    getDLLs(get_platform())
                