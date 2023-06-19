import inspect
import os

extension_dict__ = {}
commands__ = {}

class command:
    def __init__(self, aliases: list = []):
        self.aliases = aliases

    def __call__(self, func):
        global extension_dict__
        fileName = os.path.basename(inspect.getfile(func))[:-3]
        
        if fileName not in extension_dict__:
            extension_dict__[fileName] = {}

        extension_dict__[fileName][func.__name__] = func
        for alias in self.aliases:
            if alias in extension_dict__[fileName].keys():
                raise Exception(f"Duplicate alias '{alias}' in commands {func.__name__} and {extension_dict__[fileName][alias].__name__}")
            else:
                extension_dict__[fileName][alias] = func

        build_commands__()
        return func

def build_commands__():
    global extension_dict__, commands__
    commands__ = {}
    for file_commands in extension_dict__.values():
        for command_name, command_func in file_commands.items():
            if command_name in commands__:
                raise Exception(f"Duplicate alias '{command_name}' in commands {command_func.__name__} and {commands__[command_name].__name__}")
            else:
                commands__[command_name] = command_func
    print(commands__)