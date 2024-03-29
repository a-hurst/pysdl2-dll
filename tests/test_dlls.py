# -*- coding: utf-8 -*-
import os
import sys
import pytest

platform = os.getenv('SDL2DLL_PLATFORM')
manylinux = platform and 'manylinux' in platform
is_macos = sys.platform == 'darwin'
nodlls = not manylinux and sys.platform not in ('win32', 'darwin')
pytestmark = pytest.mark.skipif(nodlls, reason="No binaries for this platform")


def test_audio_backends():
    import sdl2
    from sdl2 import audio

    # Get names of all available SDL2 audio backends and devices
    backends = []
    devices = {}
    sdl2.SDL_Init(0)
    for index in range(audio.SDL_GetNumAudioDrivers()):
        # Get input/output device names for each audio driver
        drivername = audio.SDL_GetAudioDriver(index)
        backends.append(drivername.decode('utf-8'))
        # Try loading each audio driver and listing avaliable devices
        os.environ["SDL_AUDIODRIVER"] = drivername.decode('utf-8')
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO)
        driver = audio.SDL_GetCurrentAudioDriver()
        if driver is not None:
            driver = driver.decode('utf-8')
            devices[driver] = {'input': [], 'output': []}
            outnum = audio.SDL_GetNumAudioDevices(False)
            innum = audio.SDL_GetNumAudioDevices(True)
            for x in range(outnum):
                name = audio.SDL_GetAudioDeviceName(x, False)
                assert name is not None
                devices[driver]['output'].append(name.decode('utf-8'))
            for x in range(innum):
                name = audio.SDL_GetAudioDeviceName(x, True)
                assert name is not None
                devices[driver]['input'].append(name.decode('utf-8'))
        sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_AUDIO)
    sdl2.SDL_Quit()

    print("Audio backends supported by binary:")
    print(backends)

    print("\nAvailable audio drivers and devices:")
    for driver in devices.keys():
        print(driver)
        print(" - input: {0}".format(str(devices[driver]['input'])))
        print(" - output: {0}".format(str(devices[driver]['output'])))


def test_render_backends():
    import sdl2

    # Get names of all supported SDL2 render drivers
    renderers = []
    num_drivers = sdl2.SDL_GetNumRenderDrivers()
    for i in range(0, num_drivers):
        info = sdl2.render.SDL_RendererInfo()
        sdl2.SDL_GetRenderDriverInfo(i, info)
        renderers.append(info.name.decode('utf-8'))
    
    print("Available SDL2 renderers:")
    print(renderers)


def test_video_backends():
    import sdl2

    # Get names of all supported SDL2 video drivers
    backends = []
    num_drivers = sdl2.SDL_GetNumVideoDrivers()
    for i in range(0, num_drivers):
        drivername = sdl2.SDL_GetVideoDriver(i)
        backends.append(drivername.decode('utf-8'))
    
    print("Available SDL2 video backends:")
    print(backends)


def test_sdl2mixer_formats():
    import sdl2
    from sdl2 import sdlmixer

    # Get list of all supported audio formats
    sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
    supported = []
    libs = {
        'FLAC': sdlmixer.MIX_INIT_FLAC,
        'MOD': sdlmixer.MIX_INIT_MOD,
        'MP3': sdlmixer.MIX_INIT_MP3,
        'OGG': sdlmixer.MIX_INIT_OGG,
        'MID': sdlmixer.MIX_INIT_MID,
        'OPUS': sdlmixer.MIX_INIT_OPUS,
        'WAVPACK': 0x00000080 # NOTE: Replace once in pysdl2
    }
    for lib in libs.keys():
        flags = libs[lib]
        ret = sdlmixer.Mix_Init(flags)
        err = sdlmixer.Mix_GetError()
        if err:
            err = err.decode('utf-8')
            print("Error loading {0} library: {1}".format(lib, err))
            sdl2.SDL_ClearError()
        if ret & flags == flags:
            supported.append(lib)
        sdlmixer.Mix_Quit()
    sdl2.SDL_Quit()

    # Print out supported formats
    print("Supported mixer libraries:")
    print(supported)

    # Ensure all available formats supported by binaries
    assert len(supported) == len(libs.keys())


def test_sdl2image_formats():
    import sdl2
    from sdl2 import sdlimage

    sdl2.SDL_Init(0)
    supported = []
    libs = {
        'JPEG': sdlimage.IMG_INIT_JPG,
        'PNG': sdlimage.IMG_INIT_PNG,
        'TIFF': sdlimage.IMG_INIT_TIF,
        'WEBP': sdlimage.IMG_INIT_WEBP,
        'AVIF': sdlimage.IMG_INIT_AVIF,
    }
    for lib in libs.keys():
        flags = libs[lib]
        ret = sdlimage.IMG_Init(flags)
        err = sdlimage.IMG_GetError()
        if err:
            err = err.decode('utf-8')
            print("Error loading {0} library: {1}".format(lib, err))
            sdl2.SDL_ClearError()
        if ret & flags == flags:
            supported.append(lib)
        sdlimage.IMG_Quit()
    sdl2.SDL_Quit()

    # Test for and print out supported formats
    print("Supported image libraries:")
    print(supported)

    # Ensure all available formats supported by binaries
    assert len(supported) == len(libs.keys())
