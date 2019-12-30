# pysdl2-dll

PySDL2-dll is a Python package that makes it easier to install and use PySDL2 in your Python project. When you install pysdl2-dll, it fetches the official pre-compiled SDL2, SDL2\_Mixer, SDL2\_ttf, and SDL2\_image binaries, as well as unofficial pre-compiled SDL2\_gfx binaries, for the current OS and puts them inside a Python package. Then, when imported, it sets the `PYSDL2_DLL_PATH` variable to the folder inside pysdl2-dll containing the compiled DLLs for your OS so that PySDL2 will load them automatically.

## Requirements

PySDL2-dll supports retrieval/packaging of SDL2, SDL2\_Mixer, SDL2\_ttf, SDL2\_image, and SDL2\_gfx binaries for the following platforms:

* macOS (10.6+, 64-bit)
* Windows 32-bit
* Windows 64-bit

Linux is not currently supported, though support may be added later using a build system based on the manylinux Docker image and TravisCI.

Additionally, until PySDL2 0.9.7 is released, you will need to install the latest GitHub version in order for PySDL2-dll to work on macOS. If you have Git installed, you can do this by running 

```
pip install -U git+https://github.com/marcusva/py-sdl2.git
```

in a terminal window.

## Usage

Until official support is added to PySDL2, you will need to import this module manually in your Python scripts before `import sdl2` is run, e.g.:

```python
import sdl2dll
import sdl2

sdl2.ext.init()
```

Alternatively, you can install a patched version of PySDL2 from Github that imports PySDL2-dll automatically, which will allow PySDL2 projects to seamlessly load the PySDL2-dll libraries without needing to import it explicitly: 

```
pip install -U git+https://github.com/a-hurst/py-sdl2.git@sdl2dll
```
