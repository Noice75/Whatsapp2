from whatsapp import commands
import whatsapp

current_State = ['▫','▫','▫','▫','▫','▫','▫','▫','▫','▫']
default_State = ['▫','▫','▫','▫','▫','▫','▫','▫','▫','▫']
player = 1     
win = 1    
draw = -1    
running = 0    
stop = 1  
game = running    
Mark = 'X'

def displayCurrent_State():
        whatsapp.send(f"{current_State[1]}|{current_State[2]}|{current_State[3]}\n{current_State[4]}|{current_State[5]}|{current_State[6]}\n{current_State[7]}|{current_State[8]}|{current_State[9]}")
    
def CheckPosition(x):    
        if(current_State[x] == '▫'):    
                return True    
        else:    
                return False    
   
def CheckWin():    
        global game    
        if(current_State[1] == current_State[2] and current_State[2] == current_State[3] and current_State[1] != '▫'):    
                game = win    
        elif(current_State[4] == current_State[5] and current_State[5] == current_State[6] and current_State[4] != '▫'):    
                game = win    
        elif(current_State[7] == current_State[8] and current_State[8] == current_State[9] and current_State[7] != '▫'):    
                game = win  
        elif(current_State[1] == current_State[4] and current_State[4] == current_State[7] and current_State[1] != '▫'):    
                game = win    
        elif(current_State[2] == current_State[5] and current_State[5] == current_State[8] and current_State[2] != '▫'):    
                game = win    
        elif(current_State[3] == current_State[6] and current_State[6] == current_State[9] and current_State[3] != '▫'):    
                game=win   
        elif(current_State[1] == current_State[5] and current_State[5] == current_State[9] and current_State[5] != '▫'):    
                game = win    
        elif(current_State[3] == current_State[5] and current_State[5] == current_State[7] and current_State[5] != '▫'):    
                game=win   
        elif(current_State[1]!='▫' and current_State[2]!='▫' and current_State[3]!='▫' and current_State[4]!='▫' and current_State[5]!='▫' and current_State[6]!='▫' and current_State[7]!='▫' and current_State[8]!='▫' and current_State[9]!='▫'):    
                game=draw    
        else:            
                game=running

def start(owner):
        global player
        global Mark
        global current_State
        global default_State
        global stop
        global running
        global game
        global win
        global draw
        player = 1     
        win = 1    
        draw = -1    
        running = 0    
        stop = 1  
        game = running    
        Mark = 'X'
        whatsapp.send("Enter the position between [1-9]")
        while(game == running):
                displayCurrent_State()
                while True:
                        if(player % 2 != 0):
                                Mark = '❌'
                                if(owner == 'me'):
                                        x = whatsapp.wait_to_send(waitTime=30).body
                                else:
                                        x = whatsapp.wait_to_recive(waitTime=30).body
                        else:
                                Mark = '⭕'
                                if(owner == 'notme'):
                                        x = whatsapp.wait_to_send(waitTime=30).body
                                else:
                                        x = whatsapp.wait_to_recive(waitTime=30).body
                        try:
                                if(x == None):
                                        break
                                choice = int(x)
                                if(choice not in [1,2,3,4,5,6,7,8,9]):
                                        continue
                                break
                        except:
                                continue
                if(x == None):
                    break
                if(CheckPosition(choice)):    
                        current_State[choice] = Mark    
                        player+=1    
                        CheckWin()
        if(x == None):
            current_State = default_State
            return
        if(game != running):
                displayCurrent_State()
        if(game==draw):    
                whatsapp.send("Draw!")
                current_State = default_State
        elif(game==win):    
                player-=1    
                if(player%2!=0):    
                        whatsapp.send("Player X Won")
                else:    
                        whatsapp.send("Player O Won")
                current_State = default_State

################################################################################# -- End of Functions
@commands.command()
def xno(ctx):
    print("UWU")
    global current_State, default_State, player, win, draw, running, stop, game, Mark
    chatID = ctx.id
    current_State = ['▫','▫','▫','▫','▫','▫','▫','▫','▫','▫']
    default_State = ['▫','▫','▫','▫','▫','▫','▫','▫','▫','▫']
    player = 1     
    win = 1    
    draw = -1    
    running = 0    
    stop = 1  
    game = running    
    Mark = 'X'
    try:
            if('true' in chatID):
                    print("ME")
                    start(owner='me')
            else:
                    print("NOTME")
                    start(owner='notme')
    except:
            pass

def setup():
    commands.setup_extension()