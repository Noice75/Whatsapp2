import importlib
import os

built_commands = {}
prebuilt_commands = {}

class setup_extension:
    def __init__(self) -> None:
        self.classesref = {}
        pass

    def build(self):
        global prebuilt_commands
        global built_commands
        built_commands = {}
        for file_name,i in prebuilt_commands.items():
            for func_name, func_ref in i[0].items():
                if(func_name in built_commands):
                    try:
                        raise Exception(f"Duplicate alias '{func_name}' in commands {built_commands[func_name].__name__} and {prebuilt_commands[file_name][0][func_name].__name__}")
                    except AttributeError:
                        raise Exception(f"Duplicate alias '{func_name}' in commands {built_commands[func_name][0].__name__} and {prebuilt_commands[file_name][0][func_name].__name__}")
                built_commands[func_name] = func_ref
            
            for class_name, class_func in i[1].items():
                for method_name, method_ref in class_func[0].items():
                    if(method_name in built_commands):
                        try:
                            raise Exception(f"Duplicate alias '{method_name}' in commands {built_commands[method_name][0].__name__} and {method_ref.__name__}")
                        except TypeError:
                            raise Exception(f"Duplicate alias '{method_name}' in commands {built_commands[method_name].__name__} and {method_ref.__name__}")
                    try:
                        if(len(class_func) > 1):
                            built_commands[method_name] = (method_ref,class_func[1])
                        else:
                            built_commands[method_name] = (method_ref,self.classesref[class_name])
                            prebuilt_commands[file_name][1][class_name].append(self.classesref[class_name])
                    except KeyError:
                        if(len(self.classesref.keys()) > 0):
                            raise Exception(f"Missing Class {class_name} in setup of extension {file_name}")


    def setup_extension(self, classes : list = []):
        self.classesref = {}
        for i in classes:
            self.classesref[i.__class__.__name__] = i
        self.build()

def load_extension(prebuilt_commands_dict, extension_path):
    global prebuilt_commands, built_commands
    prebuilt_commands = prebuilt_commands_dict
    extension_path += ".py"
    extension_name = os.path.basename(extension_path)
    try:
        if(extension_name[:-3] in prebuilt_commands_dict.keys()):
            print(f"Extension {extension_name} already loaded!, Skipping")
            return None,None
        spec = importlib.util.spec_from_file_location(extension_name, extension_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'setup'):
            module.setup()
        else:
            raise Exception(f"{extension_name} Does not have a setup function")
        return prebuilt_commands,built_commands
    except Exception as e:
        print(f"Failed to load extension '{extension_name}': {str(e)}")
        try:
            prebuilt_commands.pop(extension_name[:-3])
            return prebuilt_commands,built_commands
        except:
            return None,None
    
def unload_extension(prebuilt_commands_dict,extension_name):
    global prebuilt_commands
    prebuilt_commands = prebuilt_commands_dict
    try:
        prebuilt_commands.pop(extension_name)
        setup_extension().build()
        return prebuilt_commands,built_commands
    except:
        print(f"{extension_name} was not loaded")
        return None,None