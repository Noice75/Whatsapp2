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

@commands.command(aliases=["Spam"])
def spam(ctx):
    num = int(ctx.body.split()[1])
    word = ctx.body[7:]
    if(num > 20):
        whatsapp.send("SPAM limited to *<= 20*")
        return
    for i in range(num):
        whatsapp.send(word)

def setup():
    commands.setup_extension()