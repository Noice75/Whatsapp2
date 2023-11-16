import whatsapp
from whatsapp import commands
import logging
import time
import os

start = time.time()
@whatsapp.on_ready
def on_ready():
    print(f"Time taken to load = {time.time() - start}s")
    whatsapp.open_message("123456789") #Testing opening chats

@whatsapp.on_message
def on_message(ctx):
    print(f"Message - {ctx.body}, {ctx.id}, {ctx.mention}")

@whatsapp.on_send
def on_send(ctx):
    print(f"Message (Send) - {ctx.body}, {ctx.id}, {ctx.mention}")

@whatsapp.on_recive
def on_recive(ctx):
    print(f"Message (Recive) - {ctx.body}, {ctx.id}, {ctx.mention}")

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

whatsapp.run(
    browser = 'Chrome',
    headless = True,
    spawn_qrwindow = True,
    terminal_qr = True,
    profile = "Default",
    waitTime = 0,
    command_classes = [],
    customDriver = None,
    profileDir = "Default",
    clean_start = False,
    log = True,
    logFile = False,
    logLevel = logging.INFO
    )