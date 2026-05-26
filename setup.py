import os
import sys
import traceback
from pathlib import Path
from contextlib import suppress
from sysconfig import get_platform
from setuptools import Command, setup
from setuptools.command.build import build

sys.path.append(".")
from getdlls import getDLLs

override = os.getenv('SDL2DLL_PLATFORM')
platform = get_platform() if not override else override


# Define custom build method that gathers platform-specific SDL binaries

class CustomCommand(Command):

    def initialize_options(self):
        self.bdist_dir = None
        self.get_dlls = False

    def finalize_options(self):
        with suppress(Exception):
            self.bdist_dir = Path(self.get_finalized_command("bdist_wheel").bdist_dir)
            self.get_dlls = True if self.bdist_dir else False

    def run(self):
        if self.get_dlls:
            # Create the bdist and binary output paths
            self.bdist_dir.mkdir(parents=True, exist_ok=True)
            dllpath = os.path.join(self.bdist_dir, 'sdl2dll', 'dll')
            os.makedirs(dllpath)

            # Get or build the necessary SDL2 DLLs for the platform
            try:
                getDLLs(platform, dllpath)
            except Exception as e:
                print(traceback.format_exc())
                raise e


class CustomBuild(build):
    sub_commands = [('build_custom', None)] + build.sub_commands


# Install the package

setup(
	packages=['sdl2dll'],
	cmdclass={'build': CustomBuild, 'build_custom': CustomCommand},
    include_package_data=True
)
