# pysdl2-dll

PySDL2-dll is a Python package that makes it easier to install and use PySDL2 in your Python project. When you install pysdl2-dll, it fetches the official pre-compiled SDL2, SDL2_Mixer, SDL2_ttf, and SDL2_image binaries for the current OS and puts them inside a Python package. Then, when imported, it sets the `PYSDL2_DLL_PATH` variable to the folder inside pysdl2-dll containing the compiled DLLs for your OS so that PySDL2 will load them automatically.

## Requirements

PySDL2-dll supports retrieval/packaging of the SDL2, SDL2_Mixer, SDL2_ttf, and SDL2_image binaries for the following platforms:

* macOS (10.6+, 32-bit/64-bit universal)
* Windows 32-bit
* Windows 64-bit

Linux is not currently supported, though support may be added later using a build system based on the manylinux Docker image and TravisCI. SDL2_gfx is currently not supported on any plaform, as it lacks official pre-compiled binaries.

## Installation

Currently, until official support is added in PySDL2, PySDL2-dll should be run with my patched version of PySDL2 that fixes bugs with loading macOS frameworks and automatically loads PySDL2-dll when imported. This means that any existing PySDL2 projects will seamlessly load the PySDL2-dll libraries without needing to import it explicitly.

```
pip install -U git+https://github.com/a-hurst/py-sdl2.git@sdl2dll
pip install -U git+https://github.com/a-hurst/pysdl2-dll.git@master
```

Running the above commands will install both PySDL2-dll and the patched PySDL2 required to properly support it.
