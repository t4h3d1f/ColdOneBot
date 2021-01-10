import discord
from ColdOneCore import CoreColors

# Interface for data models that can be expressed as a discord.Embed
class HasEmbed:

    def _setTitle(self, title):
        self.embedTitle = title
        return self

    def _setAuthor(self, author):
        self.embedAuthor = author
        return self

    def _setDescription(self, desc):
        self.embedDescription = desc
        return self

    def _setFooter(self, footer):
        self.embedFooter = footer
        return self

    def _setThumbnail(self, url):
        self.embedThumbnail = url
        return self

    def _setColor(self, color):
        self.embedColor = color
        return self

    def _setEmbedFields(self, title = None, author = None, desc = None, footer = None, url = None, color = None):
        if title:
            _setTitle(title)
        if author:
            _setAuthor(author)
        if desc:
            _setDescription(desc)
        if footer:
            _setFooter(footer)
        if url:
            _setThumbnail(url)
        if color:
            _setColor(color)
        return self

    # Method to return a fully flushed Discord embed
    def getEmbed(self) -> discord.Embed:
        if !(hasattr(self, 'embedColor')):
            _setColor(CoreColors.DefaultColor)
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
