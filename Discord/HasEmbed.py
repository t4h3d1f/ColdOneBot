import discord

from ColdOneCore import CoreColors
from Discord.HasMessage import HasMessage

# Base  for data models that can be expressed as a discord.Embed.
class HasEmbed(HasMessage):

    def setTitle(self, title):
        self.embedTitle = title
        return self

    def setAuthor(self, author):
        self.embedAuthor = author
        return self

    def setDescription(self, desc):
        self.embedDescription = desc
        return self

    def setFooter(self, footer):
        self.embedFooter = footer
        return self

    def setThumbnail(self, url):
        self.embedThumbnail = url
        return self

    def setColor(self, color):
        self.embedColor = color
        return self

    # Set all fields of the embed in bulk.
    def setEmbedFields(self, title = None, author = None, desc = None, footer = None, url = None, color = None):
        if title:
            self.setTitle(title)
        if author:
            self.setAuthor(author)
        if desc:
            self.setDescription(desc)
        if footer:
            self.setFooter(footer)
        if url:
            self.setThumbnail(url)
        if color:
            self.setColor(color)
        return self

    def clearEmbedFields(self):
        self.setTitle("")
        self.setAuthor("")
        self.setDescription("")
        self.setFooter("")
        self.setThumbnail("")
        self.setColor("")

    # Returns a fully flushed Discord embed.
    def getEmbed(self) -> discord.Embed:
        if not hasattr(self, 'embedColor'):
            setColor(CoreColors.DefaultColor)
        if hasattr(self, 'embedDescription'):
            self.embed = discord.Embed(color=self.embedColor, title=self.embedTitle, description=self.embedDescription)
        else:
            self.embed = discord.Embed(color=self.embedColor, title=self.embedTitle)
        if hasattr(self, 'embedAuthor'):
            self.embed.set_author(name=self.embedAuthor)
        if hasattr(self, 'embedFooter'):
            self.embed.set_footer(text=self.embedFooter)
        if hasattr(self, 'embedThumbnail'):
            self.embed.set_thumbnail(url=self.embedThumbnail)
        return self.embed

    # Creates and sends the embed representation of this model.
    async def sendEmbed(self, ctx) -> discord.Message:
        self.setChannel(ctx.channel)
        message = await self.getChannel().send(embed=self.getEmbed())
        self.setMessageId(message.id)
        return message

    # Removes the embed.
    # TODO: This throws an exception sometimes, don't know why
    async def clearEmbed(self):
        try:
            msg = await self.getMessage()
            if msg:
                await msg.delete()
        except:
            print("Exception from deleting message")
        finally:
            self.setMessageId(None)
            self.setChannel(None)
            self.embed = None
