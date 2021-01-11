import discord
import re
from random import randrange

from ColdOneCore import CoreColors, getConnection
from Discord.HasEmbed import HasEmbed

class Roll:
    def __init__(self, title, author=None, desc=None, footer=None, color=None, thumbnail=None):
        super().setEmbedFields(title, author, desc, footer, thumbnail, color)

    @staticmethod
    async def roll(self,message):
        pattern = re.complile("d\d{1,10}$")
        if(pattern.search(message)):
            number = int(message[1:])
            rolled = randrange(number)
            if(number == rolled): #number +1 because randrange returns [0 to num-1]
                sendmsg = "You rolled a perfect " + str(number+1) + "!"
            elif(number == 0):
                sendmsg = "You somehow rolled a 1."
            elif(number == 69):
                sendmsg = "You rolled 69. Nice."
            else:
                sendmsg = "You rolled " + str(number+1) +"."
        else:
            sendmsg = "The format is roll d<number>"
        return sendmsg