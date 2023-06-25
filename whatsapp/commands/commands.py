import inspect
import os
from . import extension

cmdD = {}
cc = {}

class decorator:
    def __init__(self, aliases: list = []):
        self.aliases = aliases
        self.func = None
        self.file_name = None

    def __call__(self, func):
        global cmdD
        self.func = func
        self.file_name = os.path.basename(inspect.getfile(func))[:-3]
        if self.file_name not in cmdD:
            cmdD[self.file_name] = [{},{}]
        self.setup_struct()

    def setup_struct(self):
        if(self.func.__name__ == self.func.__qualname__.split('.')[0]):
            if(self.func.__name__ not in cmdD[self.file_name][0]):
                cmdD[self.file_name][0][self.func.__name__] = self.func
            else:
                raise Exception(f"Duplicate alias '{self.func.__name__}' in commands {self.func.__name__} and {cmdD[self.file_name][0][self.func.__name__].__name__}")
            self.process_func()
        else:
            if(self.func.__qualname__.split('.')[0] not in cmdD[self.file_name][1]):
                cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]] = [{self.func.__name__:self.func}]
            else:
                if(self.func.__name__ not in cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]][0]):
                    cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]][0][self.func.__name__] = self.func
                else:
                    raise Exception(f"Duplicate alias '{self.func.__name__}' in commands {self.func.__name__} and {cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]][0][self.func.__name__].__name__}")
            self.process_class()
            
    def process_class(self):
        global cmdD
        for alias in self.aliases:
            if(alias in cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]]):
                raise Exception(f"Duplicate alias '{alias}' in commands {self.func.__name__} and {cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]][0][alias].__name__}")
            cmdD[self.file_name][1][self.func.__qualname__.split('.')[0]][0][alias] = self.func

    def process_func(self):
        global cmdD
        for alias in self.aliases:
            if(alias in cmdD[self.file_name][0]):
                raise Exception(f"Duplicate alias '{alias}' in commands {self.func.__name__} and {cmdD[self.file_name][0][alias].__name__}")
            cmdD[self.file_name][0][alias] = self.func

def load_extension(extension_path):
    global cmdD, cc
    testcmd, testcc= extension.load_extension(cmdD,extension_path=extension_path)
    if(testcmd != None and testcc != None):
        cmdD, cc = testcmd, testcc

def unload_extension(extension_name):
    global cmdD, cc
    testcmd,testcc = extension.unload_extension(cmdD,extension_name=extension_name)
    if(testcmd != None and testcc != None):
        cmdD, cc = testcmd, testcc

def setup_extension(classes : list = []):
    extension.setup_extension().setup_extension(classes=classes)