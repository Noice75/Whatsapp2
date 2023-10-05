import whatsapp
from whatsapp import commands
import time

@commands.command(aliases=["Search"])
def search(ctx):
    whatsapp.send("Sure!")
    whatsapp.open_message(ctx.body.split()[-1])

@commands.command(aliases=["Echo"])
def echo(ctx):
    whatsapp.send(' '.join(ctx.body.split()[1:]))

@commands.command(aliases=["Alive", "Alive?", "alive?"])
def alive(ctx):
    whatsapp.send("Yah!")

@commands.command(aliases=["Comeback","return", "Return"])
def comeback(ctx):
    whatsapp.open_message("1234567890")
    time.sleep(2)
    whatsapp.send("Here!")

def setup():
    commands.setup_extension()