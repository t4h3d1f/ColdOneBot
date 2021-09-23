import discord
from random import choice

from ColdOneCore import CoreColors
from Discord.HasEmbed import HasEmbed


class Dinner(HasEmbed):
    dinnerchoices = ["Italian",
                     "Mexican",
                     "Burger",
                     "Pizza",
                     "Chinese",
                     "Ramen",
                     "Sushi",
                     "Poke",
                     "Fried Chicken"
                     ]

    def __init__(self, title, author=None, desc=None, footer=None, color=None, thumbnail=None):
        super().setEmbedFields(title, author, desc, footer, thumbnail, color)

    @staticmethod
    async def dinner():
        return choice(Dinner.dinnerchoices)
