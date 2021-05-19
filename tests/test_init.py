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
