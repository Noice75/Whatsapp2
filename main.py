import time
import logging
import os
start = time.time()
import whatsapp
from whatsapp import commands

@whatsapp.on_ready
def onReady():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            whatsapp.load_extension(f"commands/{filename[:-3]}")
    whatsapp.open_message("1234567890")
    print(time.time() - start)

@commands.command(aliases=["Unload"])
def unload(ctx):
    file_name = ctx.body.split()[-1]
    if(whatsapp.unload_extension(file_name)):
        whatsapp.send(f"Unloaded {file_name}")

@commands.command(aliases=["Load"])
def load(ctx):
    file_name = ctx.body.split()[-1]
    if(whatsapp.load_extension(f"commands/{file_name}")):
        whatsapp.send(f"Loaded {file_name}")

@commands.command(aliases=["Reload"])
def reload(ctx):
    file_name = ctx.body.split()[-1]
    if(whatsapp.unload_extension(file_name)):
        pass
    if(whatsapp.load_extension(f"commands/{file_name}")):
        whatsapp.send(f"ReLoaded {file_name}")

@commands.command(aliases=["loadall", "Loadall"])
def loadAll(ctx):
    for file_name in os.listdir("./commands"):
        if file_name.endswith(".py"):
            whatsapp.load_extension(f"commands/{file_name[:-3]}")
    whatsapp.send("Loaded All")

@commands.command(aliases=["Unloadall"])
def unloadAll(ctx):
    for file_name in os.listdir("./commands"):
        if file_name.endswith(".py"):
            whatsapp.unload_extension(f"{file_name[:-3]}")
    whatsapp.send("UnLoaded All")

@commands.command(aliases=["Reloadall"])
def reloadall(ctx):
    for file_name in os.listdir("./commands"):
        if file_name.endswith(".py"):
            whatsapp.unload_extension(f"{file_name[:-3]}")
            whatsapp.load_extension(f"commands/{file_name[:-3]}")
    whatsapp.send("ReLoaded All")

whatsapp.run(logLevel=logging.INFO)