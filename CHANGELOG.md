# pysdl2-dll changelog

### Version 2.26.x (Unreleased)

- Updated the 'modern' Linux wheels from `manylinux_2_24` to `manylinux_2_28`. This pushes some older distros (e.g. Ubuntu < 18.04) back to the 'legacy' `manylinux2014` wheels, but adds libdecor support to the 'modern' wheels for better Wayland support.
- Removed Network Audio System (`libaudio`) support from the 'modern' Linux wheels (if this is a problem for anyone, please let me know and I'll try to re-add it).
- Added sndio and JACK audio support to the 'legacy' Linux wheels.


### Version 2.26.2

- Bumped the SDL2 binary version from 2.26.1 to 2.26.2.


### Version 2.26.1

- Bumped the SDL2 binary version from 2.26.0 to 2.26.1.


### Version 2.26.0

- Bumped the SDL2 binary version from 2.24.2 to 2.26.0.


### Version 2.24.2

- Bumped the SDL2 binary version from 2.24.1 to 2.24.2.


### Version 2.24.1

- Bumped the SDL2 binary version from 2.24.0 to 2.24.1.


### Version 2.24.0

- Bumped the SDL2 binary version from 2.0.22 to 2.24.0.


### Version 2.0.22.post1

- Bumped the SDL2\_mixer binary version from 2.0.4 to 2.6.0.
- Bumped the SDL2\_image binary version from 2.0.5 to 2.6.0.
- Bumped the SDL2\_ttf binary version from 2.0.18 to 2.20.0.
- Migrated the build system for the mixer, image, and ttf binaries to CMake.
- Added universal2 wheels for Apple Silicon Macs now that all the official binaries are ARM-native.


### Version 2.0.22

- Bumped the SDL2 binary version from 2.0.20 to 2.0.22.
- Stripped debug symbols from manylinux binaries for smaller size.
- Fixed joystick and gamecontroller subsystem support with the manylinux binaries by removing support for the libudev input backend. This is necessary because SDL2 doesn't fall back cleanly to another controller input API if libudev doesn't work, and udev seems to be famous for having problems with SDL2 binaries that aren't installed with the system package manager.


### Version 2.0.20

- Bumped the SDL2 binary version from 2.0.18 to 2.0.20.
- Bumped the SDL\_ttf binary version from 2.0.15 to 2.0.18.


### Version 2.0.18

- Bumped the SDL2 binary version from 2.0.16 to 2.0.18.
- Added support for 64-bit ARM `manylinux_2_24` wheels!
- Added libgbm support to all manylinux wheels.


### Version 2.0.16

- Bumped the SDL2 binary version from 2.0.14 to 2.0.16.
- Removed `RuntimeWarning` when importing with Microsoft Store Python, which is properly supported as of PySDL2 0.9.8.
- Increased the target for the "legacy" manylinux wheels from `manylinux2010` to `manylinux2014`, due to an incompatibility with SDL2 2.0.16's use of the `dbus` library and the very old `dbus` version included in the official `manylinux2010` images.
- Removed dynamic support for the ancient Network Audio System (libaudio) backend in the "legacy" manylinux wheels, due to the package not being available for 32-bit `manylinux2014` images.
- Added experimental dynamic support for Pipewire audio (>= 0.3) in the "modern" manylinux wheels.

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