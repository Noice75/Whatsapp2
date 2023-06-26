import inspect
import os
from . import extension

prebuilt_commands = {}
built_commands = {}

class command:
    def __init__(self, aliases: list = []):
        self.aliases = aliases
        self.func = None
        self.file_name = None

    def __call__(self, func):
        global prebuilt_commands
        self.func = func
        self.file_name = os.path.basename(inspect.getfile(func))[:-3]
        if self.file_name not in prebuilt_commands:
            prebuilt_commands[self.file_name] = [{},{}]
        self.setup_struct()

    def setup_struct(self):
        if(self.func.__name__ == self.func.__qualname__.split('.')[0]):
            if(self.func.__name__ not in prebuilt_commands[self.file_name][0]):
                prebuilt_commands[self.file_name][0][self.func.__name__] = self.func
            else:
                raise Exception(f"Duplicate alias '{self.func.__name__}' in commands {self.func.__name__} and {prebuilt_commands[self.file_name][0][self.func.__name__].__name__}")
            self.process_func()
        else:
            if(self.func.__qualname__.split('.')[0] not in prebuilt_commands[self.file_name][1]):
                prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]] = [{self.func.__name__:self.func}]
            else:
                if(self.func.__name__ not in prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]][0]):
                    prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]][0][self.func.__name__] = self.func
                else:
                    raise Exception(f"Duplicate alias '{self.func.__name__}' in commands {self.func.__name__} and {prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]][0][self.func.__name__].__name__}")
            self.process_class()
            
    def process_class(self):
        global prebuilt_commands
        for alias in self.aliases:
            if(alias in prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]]):
                raise Exception(f"Duplicate alias '{alias}' in commands {self.func.__name__} and {prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]][0][alias].__name__}")
            prebuilt_commands[self.file_name][1][self.func.__qualname__.split('.')[0]][0][alias] = self.func

    def process_func(self):
        global prebuilt_commands
        for alias in self.aliases:
            if(alias in prebuilt_commands[self.file_name][0]):
                raise Exception(f"Duplicate alias '{alias}' in commands {self.func.__name__} and {prebuilt_commands[self.file_name][0][alias].__name__}")
            prebuilt_commands[self.file_name][0][alias] = self.func

def load_extension(extension_path):
    global prebuilt_commands, built_commands
    _prebuiltcmd, _builtcmd= extension.load_extension(prebuilt_commands,extension_path=extension_path)
    if(_prebuiltcmd != None and _builtcmd != None):
        prebuilt_commands, built_commands = _prebuiltcmd, _builtcmd
        return True
    else:
        return False

def unload_extension(extension_name):
    global prebuilt_commands, built_commands
    _prebuiltcmd,_builtcmd = extension.unload_extension(prebuilt_commands,extension_name=extension_name)
    if(_prebuiltcmd != None and _builtcmd != None):
        prebuilt_commands, built_commands = _prebuiltcmd, _builtcmd
        return True
    else:
        return False

def setup_extension(classes : list = []):
    extension.setup_extension().setup_extension(classes=classes)

def get_commands():
    return built_commands