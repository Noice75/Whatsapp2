from whatsapp import commands

@commands.command()
def lmao(ctx):
    print("Lmaaao")

def setup():
    commands.setup_extension()