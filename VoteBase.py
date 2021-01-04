import discord

from Discord.HasEmbed import HasEmbed

# Defines a base object to handle tallying and creating embeds for voting.
class VoteBase(HasEmbed):

    # VoteBase constructor, sets up fields for embed creation
    def __init__(self, title, author=None, desc=None, footer=None, color=None, thumbnail=None):
        self.embedTitle = title
        if author:
            self.embedAuthor = author
        if desc:
            self.embedDescription = desc
        if footer:
            self.embedFooter = footer
        if thumbnail:
            self.embedThumbnail = thumbnail
        if color:
            self.embedColor = color

    # Creates the embed object for this vote base
    def getEmbed(self):
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

    # Sends an embed of this VoteBase to the given context.
    # Returns the discord.Message object from the embed send.
    async def sendEmbed(self, ctx):
        self.channel = ctx.channel
        sentEmbedMsg = await ctx.channel.send(embed=self.getEmbed())
        # Add reacts
        await sentEmbedMsg.add_reaction("👍")
        await sentEmbedMsg.add_reaction("👎")

        self.embedMsgId = sentEmbedMsg.id
        return sentEmbedMsg

    # Ends the vote and counts up users' reactions.
    # Returns a dictionary of the users who voted for and against.
    async def countVote(self):
        retDict = {}
        # Count of the reactions
        usersFor = []
        usersAgainst = []
        msg = await self.channel.fetch_message(self.embedMsgId)
        for curReact in msg.reactions:
            users = await curReact.users().flatten()
            if curReact.emoji == "👍":
                for user in users:
                    if not user.bot:
                        usersFor.append(user)
            elif curReact.emoji == "👎":
                for user in users:
                    if not user.bot:
                        usersAgainst.append(user)
        retDict['voteFor'] = usersFor
        retDict['voteAgainst'] = usersAgainst
        await msg.delete()
        return retDict

    # Removes the embed
    # TODO: This throws an exception sometimes, don't know why
    async def clearEmbed(self):
        try:
            msg = await self.channel.fetch_message(self.embedMsgId)
            await msg.delete()
        except:
            print("Exception from deleting message")
