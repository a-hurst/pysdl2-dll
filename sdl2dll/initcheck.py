"""Utilities for sanity-checking the pysdl2-dll environment on import."""

import os
import sys
import warnings


def pretty_warn(msg, warntype):
    """Prints a suppressable warning without stack or line info."""
    original = warnings.showwarning
    def _warning(message, category, filename, lineno, file=None, line=None):
        print(message)
    warnings.showwarning = _warning
    warnings.warn(msg, warntype)
    warnings.showwarning = original


def _is_sdist():
    """Checks whether pysdl2-dll was installed as a binary-less source dist."""
    root_path = os.path.abspath(os.path.dirname(__file__))
    dll_dir = os.path.join(root_path, 'dll')
    return os.path.isdir(dll_dir)


def _should_update_pip_for_wheels():
    """Checks whether pip needs to be updated in order to see available wheels."""
    should_update = False
    try:
        import pip
        version_str = pip.__version__
        pip_version = tuple([int(n) for n in version_str.split(".")[:2]])
    except ImportError:
        return False

    # Linux needs pip >= 19.0 to be able to fetch manylinux2010 wheels
    if sys.platform == 'linux' and pip_version < (19, 0):
        should_update = True

    # macOS 11 and up need pip >= 20.3 to be able to use wheels properly
    elif sys.platform == 'darwin':
        import platform
        mac_major_version = int(platform.mac_ver()[0].split(".")[0])
        if mac_major_version > 10 and pip_version < (20, 3):
            should_update = True

    return should_update


def init_check():
    """Checks the pysdl2-dll environment and warns about any important issues."""
    sdist_msg = (
        "UserWarning: pysdl2-dll is installed as source-only, meaning that "
        "it does not contain any binaries and will be ignored by PySDL2."
    )
    pip_update_msg = (
        "NOTE: Binary SDL2 wheels may be available for this platform. Please "
        "update pip to the latest version and try reinstalling pysdl2-dll."
    )
    if _is_sdist():
        msg = sdist_msg
        if _should_update_pip_for_wheels():
            msg += "\n\n" + pip_update_msg
        pretty_warn(msg, UserWarning)
