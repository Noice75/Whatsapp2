text = 'Lol'
htmlt = '<img crossorigin="anonymous" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="💀" draggable="false" class="b67 emoji wa _11JPr selectable-text copyable-text" data-plain-text="💀" tabindex="-1" style="background-position: -40px -80px;"><img crossorigin="anonymous" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="💀" draggable="false" class="b67 emoji wa _11JPr selectable-text copyable-text" data-plain-text="💀" tabindex="-1" style="background-position: -40px -80px;">Lol'

import emoji
char = ""
def is_emoji(s):
    return emoji.emoji_count(s) > 0
index = 0
while True:
    try:
        str = text[index]
    except:
        try:
            if(htmlt[len(text):][0] == "<"):
                str = ""
            else:
                break
        except:
            break
    if(htmlt[index] != str):
        emoji_found = False
        htmlt = htmlt[index:]
        for i in range(len(htmlt)):
            if(is_emoji(htmlt[i]) and not emoji_found):
                char+=htmlt[i]
                emoji_found = True
            elif(emoji_found and htmlt[i] == ">"):
                htmlt = text[:index]+htmlt[i+1:]
                if(index != 0):
                    char+=str
                break
    else:
        char += str
        index += 1
print(char)