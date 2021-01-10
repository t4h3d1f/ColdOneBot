import discord

from Discord.HasEmbed import HasEmbed

# Defines a base object to handle tallying and creating embeds for voting.
class VoteBase(HasEmbed):

    # VoteBase constructor, sets up fields for embed creation
    def __init__(self, title, author=None, desc=None, footer=None, color=None, thumbnail=None):
        super().setEmbedFields(title, author, desc, footer, thumbnail, color)

    # Sends an embed of this VoteBase to the given context.
    # Returns the discord.Message object from the embed send.
    async def sendEmbed(self, ctx, isClosingEmbed=False):
        msg = await super().sendEmbed(ctx)
        # Add reacts
        if not isClosingEmbed:
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        return msg

    # Ends the vote and counts up users' reactions.
    # Returns a dictionary of the users who voted for and against.
    async def countVote(self):
        retDict = {}
        # Count of the reactions
        usersFor = []
        usersAgainst = []
        msg = await self.getMessage()
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
        await self.clearEmbed()
        return retDict
