from whatsapp import commands
import whatsapp
import random

@commands.command(aliases=["Numguess"])
def numguess(ctx):
    ctx = ctx.body.split()
    if(len(ctx) != 4):
           whatsapp.send("Start, end, number of lives not defined!")
           return
    start = int(ctx[1])
    end = int(ctx[2])
    lives = int(ctx[3])
    whatsapp.send(f"Guess a number between [{start} - {end}]")
    c_Lives = lives
    x = random.randint(start,end)
    while c_Lives > 0:
            data = whatsapp.wait_for_message(waitTime=30).body
            if(data == None):
                    return
            try:
                    y = int(data)
            except:
                    continue
            if(y <= end):
                    if(y >= start):
                            if(y == x):
                                    whatsapp.send("Correct!")
                                    break
                            else:
                                    c_Lives -= 1
                                    if(c_Lives == 0):
                                            whatsapp.send(f"Game Over!\nAns was {x}")
                                    else:
                                            whatsapp.send(f"Nope!, You have {c_Lives} lives left!")
        

def setup():
    commands.setup_extension()