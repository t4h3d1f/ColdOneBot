import discord
import re
from random import randrange

from ColdOneCore import CoreColors
from Discord.HasEmbed import HasEmbed


class Roll(HasEmbed):

    def __init__(self, title, author=None, desc=None, footer=None, color=None, thumbnail=None):
        super().setEmbedFields(title, author, desc, footer, thumbnail, color)

    @staticmethod
    async def roll(message):

        # pattern = re.complile("d\d{1,10}$")
        # if(pattern.search(message)):
        # number = int(message[1:])
        number = message
        rolled = randrange(1, number)
        # number +1 because randrange returns [0 to num-1]
        if(number == rolled):
            sendmsg = "You rolled a perfect " + str(number+1) + "!"
        elif(rolled == 0):
            sendmsg = "You somehow rolled a 1."
        elif(rolled == 69):
            sendmsg = "You rolled 69. Nice."
        else:
            sendmsg = "You rolled " + str(rolled+1) + "."
        # else:
        #     sendmsg = "The format is roll d<number>"
        return sendmsg
