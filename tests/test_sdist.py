# -*- coding: utf-8 -*-
import os
import sys
import pytest

platform = os.getenv('SDL2DLL_PLATFORM')
manylinux = platform and 'manylinux' in platform
nodlls = not manylinux and sys.platform not in ('win32', 'darwin')
pytestmark = pytest.mark.skipif(not nodlls, reason="Using binary wheel, not sdist")


def test_import():
    # Test basic sdist warning
    orig_path = os.getenv('PYSDL2_DLL_PATH')
    with pytest.warns(UserWarning):
        import sdl2dll
    # Ensure that sdist doesn't change DLL path
    assert orig_path == os.getenv('PYSDL2_DLL_PATH')
