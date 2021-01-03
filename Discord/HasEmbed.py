import discord

# Interface for data models that can be expressed as a discord.Embed
class HasEmbed:

    # Method to return a fully flushed Discord embed
    def getEmbed(self) -> discord.Embed:
        pass
