# pysdl2-dll

[![Build Status](https://api.cirrus-ci.com/github/a-hurst/pysdl2-dll.svg)](https://cirrus-ci.com/github/a-hurst/pysdl2-dll)
[![Build Status](https://ci.appveyor.com/api/projects/status/lnwpe9v50bne3afu?svg=true)](https://ci.appveyor.com/project/a-hurst/pysdl2-dll)

pysdl2-dll is a Python package that bundles the SDL2 binaries in pip-installable form for macOS and Windows, making it easier to create and run scripts/packages that use the [PySDL2](https://github.com/py-sdl/py-sdl2) library.

It uses the official SDL2, SDL2\_mixer, SDL2\_ttf, and SDL2\_image binaries for macOS and Windows, as well as [unofficial SDL2\_gfx binaries](https://github.com/a-hurst/sdl2gfx-builds) for the same platforms. For Linux, the SDL2 binaries and their dependencies are all built from source using the official Python [manylinux](https://github.com/pypa/manylinux) images for maximum compatibility.

The latest release includes the following versions of the SDL2 binaries:

SDL2 | SDL2\_ttf | SDL2\_mixer | SDL2\_image | SDL2\_gfx
--- | --- | --- | --- | ---
2.30.10 | 2.22.0 | 2.8.0 | 2.8.2 | 1.0.4


## Installation

You can install the latest version of pysdl2-dll via pip:

```bash
pip install pysdl2-dll # install latest release version
```


## Requirements

At present, the following platforms are supported:

* macOS (10.11+, 64-bit x86)
* macOS (11.0+, 64-bit ARM)
* Windows (32-bit x86)
* Windows (64-bit x86)
* Linux (32-bit x86)
* Linux (64-bit x86)
* Linux (64-bit ARM)

The pysdl2-dll package can be *installed* on platforms other than the ones listed above, but it won't have any effect.

pysdl2-dll requires PySDL2 0.9.7 or later in order to work correctly. To update to the latest PySDL2, you can run:

```bash
pip install -U pysdl2
```

Because the wheels are not built against any specfic version of Python, pysdl2-dll supports all versions and implementations of Python that are supported by PySDL2.


### Linux Requirements

There are currently two versions the Linux wheels: "legacy" wheels based on the `manylinux2014` standard (for 32-bit and 64-bit x86), and "modern" wheels based on the `manylinux_2_28` standard (for 64-bit x86 and 64-bit ARM only). The `manylinux_2_28` SDL2 binaries require a more recent version of Linux, but offer dynamic support for additional features such as native Wayland windowing, Pipewire audio, and Vulkan rendering.

You must have pip 19.3 or newer to install the `manylinux2014` wheels, and pip 20.3 or newer to install the `manylinux_2_28` wheels. Distributions that use musl C instead of glibc (e.g. Alpine Linux) are not supported.


## Usage

If you are using PySDL2 0.9.7 or later, you don't need to do anything special to use the pysdl2-dll binaries in your project: PySDL2 will load them automatically (and print a message indicating such) if they are available.

To override pysdl2-dll and use a different set of binaries, you can set the `PYSDL2_DLL_PATH` environment variable to the path of the folder containing the binaries you want to use instead, or alternatively set it to "system" to force PySDL2 to use the system install of SDL2 if available (e.g. SDL2 installed with `brew` on macOS).
