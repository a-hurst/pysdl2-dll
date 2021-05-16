# -*- coding: utf-8 -*-
import os
import sys
import pytest

platform = os.getenv('SDL2DLL_PLATFORM')
manylinux = platform and 'manylinux' in platform
nodlls = not manylinux and sys.platform not in ('win32', 'darwin')
pytestmark = pytest.mark.skipif(nodlls, reason="No binaries for this platform")


# Basic tests for making sure libraries load at all

def test_sdl2():
    import sdl2


def test_sdl2mixer():
    import sdl2.sdlmixer


def test_sdl2ttf():
    import sdl2.sdlttf


def test_sdl2image():
    import sdl2.sdlimage


def test_sdl2gfx():
    import sdl2.sdlgfx


def test_sdl2init():
    import sdl2.ext
    sdl2.ext.init()


def test_version():
    import sdl2
    import sdl2dll
    pkg_version = sdl2dll.__version__
    dll_version = sdl2.dll.version
    dll_version_str = sdl2.dll.dll._version_int_to_str(dll_version)
    assert pkg_version in dll_version_str


# Tests for checking the feature support of the SDL2 binaries

def test_audio_backends():
    import sdl2
    from sdl2 import audio

    # Get names of all available SDL2 audio drivers
    devices = {}
    sdl2.SDL_Init(0)
    for index in range(audio.SDL_GetNumAudioDrivers()):
        # Get input/output device names for each audio driver
        drivername = audio.SDL_GetAudioDriver(index)
        os.environ["SDL_AUDIODRIVER"] = drivername.decode("utf-8")
        # Need to reinitialize subsystem for each driver
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO)
        driver = audio.SDL_GetCurrentAudioDriver()
        if driver is not None:
            driver = driver.decode("utf-8")
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

    print("Available audio drivers and devices:")
    for driver in devices.keys():
        print(driver)
        print(" - input: {0}".format(str(devices[driver]['input'])))
        print(" - output: {0}".format(str(devices[driver]['output'])))


def test_render_backends():
    import sdl2

    print("\nAvailable SDL2 renderers:")
    num_drivers = sdl2.SDL_GetNumRenderDrivers()
    for i in range(0, num_drivers):
        info = sdl2.render.SDL_RendererInfo()
        sdl2.SDL_GetRenderDriverInfo(i, info)
        print(" - " + info.name.decode('utf-8'))


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
        'OPUS': sdlmixer.MIX_INIT_OPUS
    }
    for lib in libs.keys():
        flags = libs[lib]
        ret = sdlmixer.Mix_Init(flags)
        err = sdlmixer.Mix_GetError()
        if err:
            print("Error loading {0} library: {1}".format(lib, err))
        if ret & flags == flags:
            supported.append(lib)
        sdlmixer.Mix_Quit()

    # Test for and print out supported formats
    assert len(supported) # only fail if none supported
    print("Supported mixer libraries:")
    print(supported)
    sdl2.SDL_Quit()


def test_sdl2image_formats():
    import sdl2
    from sdl2 import sdlimage

    sdl2.SDL_Init(0)
    supported = []
    libs = {
        'JPEG': sdlimage.IMG_INIT_JPG,
        'PNG': sdlimage.IMG_INIT_PNG,
        'TIFF': sdlimage.IMG_INIT_TIF,
        'WEBP': sdlimage.IMG_INIT_WEBP
    }
    for lib in libs.keys():
        flags = libs[lib]
        ret = sdlimage.IMG_Init(flags)
        err = sdlimage.IMG_GetError()
        if err:
            print("Error loading {0} library: {1}".format(lib, err))
        if ret & flags == flags:
            supported.append(lib)
        sdlimage.IMG_Quit()

    # Test for and print out supported formats
    assert len(supported) # only fail if none supported
    print("Supported image libraries:")
    print(supported)
    sdl2.SDL_Quit()