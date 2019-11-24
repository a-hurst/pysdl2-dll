"""Adds the SDL2 DLLs in the package to the PySDL2 DLL search path"""

__version__ = "2.0.10"

import os

dll_path = os.getenv('PYSDL2_DLL_PATH')
if dll_path == None:
	root_path = os.path.abspath(os.path.dirname(__file__))
	dll_path = os.path.join(root_path, 'dll')
	os.environ['PYSDL2_DLL_PATH'] = dll_path
    