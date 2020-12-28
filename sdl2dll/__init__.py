"""Adds the SDL2 DLLs in the package to the PySDL2 DLL search path"""

__version__ = "2.0.14"

import os


def get_dllpath():
	root_path = os.path.abspath(os.path.dirname(__file__))
	return os.path.join(root_path, 'dll')

dll_path = os.getenv('PYSDL2_DLL_PATH')
if dll_path == None:
	os.environ['PYSDL2_DLL_PATH'] = get_dllpath()
