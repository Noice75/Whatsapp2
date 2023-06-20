import importlib
import os

def load_extension(dict,extension_path):
    extension_path += ".py"
    extension_name = os.path.basename(extension_path)
    try:
        if(extension_name[:-3] in dict.keys()):
            print("Extension already loaded!, Skipping")
            return
        spec = importlib.util.spec_from_file_location(extension_name, extension_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"Failed to load extension '{extension_name}': {str(e)}")

def unload_extension(dict,extension_name):
    try:
        dict.pop(extension_name)
        return dict
    except:
        print(f"{extension_name} was never loaded!")