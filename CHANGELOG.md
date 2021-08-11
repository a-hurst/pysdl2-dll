# pysdl2-dll changelog

### Version 2.0.16

- Bumped the SDL2 binary version from 2.0.14 to 2.0.16.
- Removed `RuntimeWarning` when importing with Microsoft Store Python, which is properly supported as of PySDL2 0.9.8.
- Increased the target for the "legacy" manylinux wheels from `manylinux2010` to `manylinux2014`, due to an incompatibility with SDL2 2.0.16's use of the `dbus` library and the very old `dbus` version included in the official `manylinux2010` images.
- Removed dynamic support for the ancient Network Audio System (libaudio) backend in the "legacy" manylinux wheels, due to the package not being available for 32-bit `manylinux2014` images.

### Version 2.0.14.post2

- Added support for Linux (x86, 32-bit and 64-bit), using the official `manylinux` images to build SDL2 and its companion libraries from source.
- Added an informative `RuntimeWarning` when imported with the Microsoft Store version of Python, which is currently incompatible with the way dependency libraries for SDL\_image, SDL\_TTF, and SDL\_mixer are bundled in pysdl2-dll.
- Added an informative `UserWarning` when using a binary-less install of pysdl2-dll.
- Added an additional `UserWarning` when using a binary-less install of pysdl2-dll on a platform that might be able to use wheels with a more recent version of pip.


### Version 2.0.14.post1

- Fixed bug where pysdl2-dll reported the wrong version.


### Version 2.0.14

- Bumped the SDL2 binary version from 2.0.12 to 2.0.14.
- Fixed inclusion of SDL2 license file in wheels and source distribution.


### Version 2.0.12

- Bumped the SDL2 binary version from 2.0.10 to 2.0.12.


### Version 2.0.10

- Initial release, packaging the following SDL2 binaries for Windows (32-bit and 64-bit) and macOS:

SDL2 | SDL2\_ttf | SDL2\_mixer | SDL2\_image | SDL2_gfx
--- | --- | --- | --- | ---
2.0.10 | 2.0.15 | 2.0.4 | 2.0.5 | 1.0.4