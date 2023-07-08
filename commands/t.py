import whatsapp
from whatsapp import commands

@commands.command(aliases=["Search"])
def search(ctx):
    whatsapp.openChat(ctx.body.split()[-1])

@commands.command(aliases=["Echo"])
def echo(ctx):
    whatsapp.send(' '.join(ctx.body.split()[1:]))

@commands.command(aliases=["Alive", "Alive?", "alive?"])
def alive(ctx):
    whatsapp.send("Yah!")

def setup():
    commands.setup_extension()