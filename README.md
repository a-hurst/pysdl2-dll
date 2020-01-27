# pysdl2-dll

[![Build Status](https://travis-ci.org/a-hurst/pysdl2-dll.svg?branch=master)](https://travis-ci.org/a-hurst/pysdl2-dll)
[![Build status](https://ci.appveyor.com/api/projects/status/lnwpe9v50bne3afu?svg=true)](https://ci.appveyor.com/project/a-hurst/pysdl2-dll)

pysdl2-dll is a Python package that bundles the SDL2 binaries in pip-installable form for macOS and Windows, making it easier to create and run scripts/packages that use the [PySDL2](https://github.com/marcusva/py-sdl2) library. When imported, it sets the `PYSDL2_DLL_PATH` variable to point to the SDL2 binaries inside the pysdl2-dll package, allowing PySDL2 to find and load them automatically without any external installation required. 

pysdl2-dll uses the official SDL2, SDL2\_Mixer, SDL2\_ttf, and SDL2\_image binaries for macOS and Windows, as well as [unofficial SDL2\_gfx binaries](https://github.com/a-hurst/sdl2gfx-builds) for the same platforms.

## Requirements

At present, the following platforms are supported:

* macOS (10.6+, 64-bit)
* Windows 32-bit
* Windows 64-bit

Linux is not currently supported as no official binaries are available, though support may be added in future. The pysdl2-dll package can be *installed* on Linux and other unsupported platforms without issue, but it won't have any effect.

pysdl2-dll requires PySDL2 0.9.7 or later in order to work correctly on macOS, and to be loaded automatically by PySDL2 when available.

## Usage

As of PySDL2 0.9.7, pysdl2-dll binaries will be used automatically when `import sdl2` is run unless `PYSDL2_DLL_PATH` is explicitly set in the environment. For older versions of PySDL2, you will need to import this module manually in your Python scripts before `import sdl2` is run, e.g.:

```python
import sdl2dll
import sdl2

sdl2.ext.init()
```

To override pysdl2-dll you can set the `PYSDL2_DLL_PATH` environment variable to a different path containing SDL2 binaries, or to "system" to force use of system SDL2 libraries (if available), e.g.:

```bash
export PYSDL2_DLL_PATH=system # on macOS and Linux
```

```powershell
set PYSDL2_DLL_PATH=system # on Windows (for current session only)
setx PYSDL2_DLL_PATH=system # on Windows (for all future sessions)
```