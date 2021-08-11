#!/bin/bash
set -e -u -x


# Install required and optional dependencies for SDL2 so that it compiles with support
# for as many different audio/video/input backends as possible

if command -v yum &> /dev/null; then
    # For manylinux2014 and earlier (based on CentOS)
    yum install -y libtool epel-release

    # Install audio libraries and backends (ALSA, PulseAudio, JACK, NAS, libsamplerate)
    yum install -y alsa-lib-devel pulseaudio-libs-devel jack-audio-connection-kit-devel \
        nas-devel libsamplerate-devel

    # Install X11 and related libraries
    yum install -y libX11-devel libXext-devel libXrandr-devel libXcursor-devel \
        libXinerama-devel libXi-devel libXxf86vm-devel libXScrnSaver-devel

    # Install OpenGL renderers (OpenGL, OpenGL ES v2)
    yum install -y mesa-libGL-devel mesa-libEGL-devel

    # Install input libraries
    yum install -y dbus-devel libudev-devel libusb-devel ibus-devel

else
    # For manylinux_2_24 and later (based on Debian)
    apt-get update
    apt-get install -y libtool 

    # Install audio libraries and backends (ALSA, PulseAudio, JACK, sndio, NAS, libsamplerate)
    apt-get install -y libasound2-dev libpulse-dev libjack-jackd2-dev libsndio-dev \
        libaudio-dev libsamplerate0-dev

    # Install X11, Wayland, and related libraries
    apt-get install -y libx11-dev libxext-dev libxrandr-dev libxcursor-dev \
        libxinerama-dev libxi-dev libxxf86vm-dev libxss-dev libwayland-dev

    # Install OpenGL renderers (OpenGL, OpenGL ES v1, OpenGL ES v2)
    apt-get install -y libgl1-mesa-dev libgles1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev

    # Install input libraries
    apt-get install -y libdbus-1-dev libudev-dev libusb-1.0-0-dev libibus-1.0-dev \
        fcitx-libs-dev libxkbcommon-dev

fi


# Compile SDL2, addon libraries, and any necessary dependencies

if [ -d "/io" ]; then
    cd /io
fi
/opt/python/cp37-cp37m/bin/python -u setup.py bdist_wheel


# Run unit tests on built pysdl2-dll wheel

export SDL_VIDEODRIVER="dummy"
export SDL_AUDIODRIVER="dummy"
export PYTHONFAULTHANDLER=1
/opt/python/cp37-cp37m/bin/python -m pip install -U --force-reinstall --no-index --find-links=./dist pysdl2-dll
/opt/python/cp37-cp37m/bin/python -m pip install pytest git+https://github.com/marcusva/py-sdl2.git
/opt/python/cp37-cp37m/bin/pytest -v -rP
