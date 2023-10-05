from whatsapp import commands
import whatsapp

@commands.command()
def lmao(ctx):
    # whatsapp.send("Chup")
    # ctx = whatsapp.wait_to_send(waitTime=10)
    x = "numguess 1 20 5"
    print(x[9:].split())
    # whatsapp.send(f"Bola na chup fir ye wapas kyu bheja\n *{ctx.body}*")

def setup():
    commands.setup_extension()