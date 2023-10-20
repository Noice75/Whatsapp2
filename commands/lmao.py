from whatsapp import commands
import whatsapp

@commands.command()
def lmao(ctx):
    whatsapp.send("Waiting")
    ctx = whatsapp.wait_for_id(ctx.mention[0])
    whatsapp.send(f"Message - {ctx.body}, {ctx.id}, {ctx.mention}")

def setup():
    commands.setup_extension()