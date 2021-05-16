#!/bin/bash
set -e -u -x

# Define manylinux version
export SDL2DLL_PLATFORM=manylinux2010

# Install required and optional dependencies for SDL2 so that it compiles with support
# for different audio/video/input backends
yum install -y libtool alsa-lib-devel pulseaudio-libs-devel libX11-devel \
    libXext-devel libXrandr-devel libXcursor-devel libXi-devel libXinerama-devel \
    libXxf86vm-devel libXScrnSaver-devel mesa-libGL-devel dbus-devel libudev-devel \
    mesa-libEGL-devel libsamplerate-devel libusb-devel ibus-devel

# Compile SDL2, addon libraries, and any necessary dependencies
cd /io
/opt/python/cp37-cp37m/bin/python -u setup.py bdist_wheel

# Copy built manylinux wheel to a new folder
mkdir /io/wheels
cp -r dist/* /io/wheels