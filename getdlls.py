import os
import sys
import shutil
import subprocess as sub
from zipfile import ZipFile 
from wheel.pep425tags import get_platform

try:
    from urllib.request import urlopen # Python 3.x
except ImportError:
    from urllib2 import urlopen # Python 2


libraries = ['SDL2', 'SDL2_mixer', 'SDL2_ttf', 'SDL2_image', 'SDL2_gfx']

sdl2_urls = {
    'macOS': {
        'SDL2': 'https://www.libsdl.org/release/SDL2-2.0.10.dmg',
        'SDL2_mixer': 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.4.dmg',
        'SDL2_ttf': 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.15.dmg',
        'SDL2_image': 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.5.dmg',
        'SDL2_gfx': 'https://github.com/a-hurst/sdl2gfx-builds/releases/download/1.0.4/SDL2_gfx-1.0.4.dmg'
    },
    'win32': {
        'SDL2': 'https://www.libsdl.org/release/SDL2-2.0.10-win32-x86.zip',
        'SDL2_mixer': 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.4-win32-x86.zip',
        'SDL2_ttf': 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.15-win32-x86.zip',
        'SDL2_image': 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.5-win32-x86.zip',
        'SDL2_gfx': 'https://github.com/a-hurst/sdl2gfx-builds/releases/download/1.0.4/SDL2_gfx-1.0.4-win32-x86.zip'
    },
    'win64': {
        'SDL2': 'https://www.libsdl.org/release/SDL2-2.0.10-win32-x64.zip',
        'SDL2_mixer': 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.4-win32-x64.zip',
        'SDL2_ttf': 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.15-win32-x64.zip',
        'SDL2_image': 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.5-win32-x64.zip',
        'SDL2_gfx': 'https://github.com/a-hurst/sdl2gfx-builds/releases/download/1.0.4/SDL2_gfx-1.0.4-win32-x64.zip'
    }
}


def getDLLs(platform_name):
    
    dlldir = os.path.join('sdl2dll', 'dll')
    licensedir = os.path.join('sdl_licenses')
    for d in ['temp', dlldir, licensedir]:
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.mkdir(d)
    
    
    if 'macosx' in platform_name:
        
        for lib in libraries:
            
            mountpoint = '/tmp/' + lib
            dllname = lib + '.framework'
            dllpath = os.path.join(mountpoint, dllname)
            dlloutpath = os.path.join(dlldir, dllname)
            licensepath = os.path.join(mountpoint, 'ReadMe.txt')
            licensepath2 = os.path.join(mountpoint, 'License.txt')
            licenseoutpath = os.path.join(licensedir, 'LICENSE.{0}.txt'.format(lib))
            
            dmg = urlopen(sdl2_urls['macOS'][lib])
            outpath = os.path.join('temp', lib + '.dmg')
            with open(outpath, 'wb') as out:
                out.write(dmg.read())
                
            sub.check_call(['hdiutil', 'attach', outpath, '-mountpoint', mountpoint])
            if os.path.exists(licensepath2): # for sdl2_gfx
                licensepath = licensepath2
            shutil.copy(licensepath, licenseoutpath)
            shutil.copytree(dllpath, dlloutpath, symlinks=True)
            sub.call(['hdiutil', 'unmount', mountpoint])

            extraframeworkpath = os.path.join(dlloutpath, 'Versions', 'A', 'Frameworks')
            if os.path.exists(extraframeworkpath):
                for f in os.listdir(extraframeworkpath):
                    resourcepath = os.path.join(extraframeworkpath, f, 'Resources')
                    if os.path.exists(resourcepath):
                        for name in os.listdir(resourcepath):
                            if 'LICENSE' in name:
                                licencepath = os.path.join(resourcepath, name)
                                outpath = os.path.join(licensedir, name)
                                shutil.copyfile(licencepath, outpath)

            
    elif platform_name in ['win32', 'win_amd64']:
        
        arch = 'win64' if platform_name == 'win_amd64' else 'win32'
        
        for lib in libraries:
            
            dllzip = urlopen(sdl2_urls[arch][lib])
            outpath = os.path.join('temp', lib + '.zip')
            with open(outpath, 'wb') as out:
                out.write(dllzip.read())
            
            with ZipFile(outpath, 'r') as z:
                for name in z.namelist():
                    if name[-4:] == '.dll':
                        z.extract(name, dlldir)
                    elif 'LICENSE' in name:
                        z.extract(name, licensedir)
                    elif 'README' in name:
                        z.extract(name, licensedir)
                        oldname = os.path.join(licensedir, name)
                        newname = os.path.join(licensedir, 'LICENSE.{0}.txt'.format(lib))
                        os.rename(oldname, newname)
                    
                        
    else:

        dummyfile = os.path.join(dlldir, '.unsupported')
        with open(dummyfile, 'w') as f:
            f.write("No dlls available for this platform!")

    shutil.rmtree('temp')
        

if __name__ == '__main__':
    getDLLs(get_platform())
                