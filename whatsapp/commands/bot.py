import importlib
import os
from .command import *


__loaded_extensions = []

def load_extension(extension_path):
    extension_path += ".py"
    global __loaded_extensions
    extension_name = os.path.basename(extension_path)
    try:
        if(extension_name in __loaded_extensions):
            print("Extension already loaded!, Skipping")
            return
        spec = importlib.util.spec_from_file_location(extension_name, extension_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        __loaded_extensions.append(extension_name[:-3])
    except Exception as e:
        print(f"Failed to load extension '{extension_name}': {str(e)}")

def unload_extension(extension_name):
    global __loaded_extensions
    try:
        __loaded_extensions.pop(__loaded_extensions.index(extension_name))
        extension_dict__.pop(extension_name)
        build_commands__()
    except:
        print(f"{extension_name} was never loaded!")