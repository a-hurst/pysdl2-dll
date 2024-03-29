#!/bin/bash
set -e -u -x


# Initialize the PATH and initial directory

export PATH=/opt/python/cp310-cp310/bin:$PATH

if [ -d "/io" ]; then
    cd /io
fi


# Install required and optional dependencies for SDL2 so that it compiles with support
# for as many different audio/video/input backends as possible

if command -v yum &> /dev/null; then
    # For manylinux2014 & manylinux_2_28 (based on CentOS)
    yum install -y libtool dbus-devel nasm

    # Install additional audio backends from source
    if [[ "$AUDITWHEEL_POLICY" == "manylinux_2_28" ]]; then

        # Install pipewire >= 0.3.20 from source for manylinux_2_28
        python3.10 -m pip install meson ninja
        python3.10 build_extras.py pipewire

    elif [[ "$AUDITWHEEL_POLICY" == "manylinux2014" ]]; then

        # Install JACK v1 from source for manylinux2014
        yum install -y libdb-devel
        python3.10 build_extras.py jack1

    fi

    # Install audio libraries and backends (ALSA, PulseAudio, libsamplerate)
    yum install -y alsa-lib-devel pulseaudio-libs-devel libsamplerate-devel

    # Build sndio from source
    python3.10 build_extras.py sndio

    # Install X11 and related libraries
    yum install -y libX11-devel libXext-devel libXrandr-devel libXcursor-devel \
        libXfixes-devel libXi-devel libXinerama-devel libXxf86vm-devel \
        libXScrnSaver-devel

    # Install OpenGL renderers (OpenGL, OpenGL ES v2)
    yum install -y mesa-libGL-devel mesa-libGLES-devel mesa-libEGL-devel \
        mesa-libgbm-devel libdrm-devel

    # Install input libraries
    yum install -y libudev-devel ibus-devel systemd-devel libxkbcommon-devel \
        libusb-devel

    # Install additional libraries for manylinux_2_28
    if [[ "$AUDITWHEEL_POLICY" == "manylinux_2_28" ]]; then

        # Install Wayland/Vulkan libraries
        yum install -y wayland-devel wayland-protocols-devel vulkan-devel

        # Install libdecor from source
        yum install -y pango-devel
        python3.10 build_extras.py libdecor

    fi

else
    # For manylinux_2_24 (based on Debian)
    apt-get update
    apt-get install -y libtool libdbus-1-dev

    # Install Pipewire from source (done before other audio backends to minimize build time)
    export PIPEWIRE_VERSION=0.3.33
    export PIPEWIRE_URL=https://gitlab.freedesktop.org/pipewire/pipewire/-/archive
    python3.10 -m pip install meson ninja
    curl $PIPEWIRE_URL/$PIPEWIRE_VERSION/pipewire-$PIPEWIRE_VERSION.tar.gz | tar -xz
    cd pipewire-$PIPEWIRE_VERSION
    ./autogen.sh --prefix=/usr
    make && make install
    cd ..

    # Install audio libraries and backends (ALSA, PulseAudio, JACK, sndio, NAS, libsamplerate)
    apt-get install -y libasound2-dev libpulse-dev libaudio-dev libjack-dev libsndio-dev \
        libsamplerate0-dev

    # Install X11, Wayland, and related libraries
    apt-get install -y libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxfixes-dev \
        libxi-dev libxinerama-dev libxxf86vm-dev libxss-dev libwayland-dev

    # Install OpenGL renderers (OpenGL, OpenGL ES v1, OpenGL ES v2)
    apt-get install -y libgl1-mesa-dev libgles1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev

    # Install input libraries
    apt-get install -y libdbus-1-dev libudev-dev libusb-1.0-0-dev libibus-1.0-dev \
        fcitx-libs-dev libxkbcommon-dev

    # Update Wayland to a supported version (=> 1.18.0 required as of SDL 2.0.22)
    apt-get install -y libffi-dev libxml2-dev
    export WAYLAND_VERSION=1.20.0
    export WAYLAND_URL=https://gitlab.freedesktop.org/wayland/wayland/-/archive
    curl $WAYLAND_URL/$WAYLAND_VERSION/wayland-$WAYLAND_VERSION.tar.gz | tar -xz
    cd wayland-$WAYLAND_VERSION
    meson build --buildtype=release -Ddocumentation=false
    ninja -C build/ install
    cd ..

fi


# If this is a tagged release, set env to strip the debug symbols from the binaries

if [ ! -z ${CIRRUS_TAG:-} ]; then
    export SDL2DLL_RELEASE=1
    echo "Building version ${CIRRUS_TAG} for release"
fi


# Compile SDL2, addon libraries, and any necessary dependencies

#python3.10 -m pip install requests
python3.10 -u setup.py bdist_wheel


# Run unit tests on built pysdl2-dll wheel

export SDL_VIDEODRIVER="dummy"
export SDL_AUDIODRIVER="dummy"
export SDL_MIXER_DEBUG_MUSIC_INTERFACES=1
python3.10 -m pip install -U --force-reinstall --no-index --find-links=./dist pysdl2-dll
python3.10 -m pip install pytest git+https://github.com/py-sdl/py-sdl2.git
pytest -v -rP
