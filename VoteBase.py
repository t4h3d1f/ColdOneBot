import discord

from Discord.HasEmbed import HasEmbed

class VoteBase(HasEmbed):

    def __init__(self, title = "", author = "", desc = "", footer = "", )

    # Sends an embed of this VoteBase to the given context.
    # Returns the discord.Message object from the embed send.
    def sendEmbed(self, ctx):
        self.channel = ctx.channel
        sentEmbedMsg = await ctx.channel.send(embed=self.getEmbed())
        # Add reacts
        await sentEmbedMsg.add_reaction("👍")
        await sentEmbedMsg.add_reaction("👎")

        self.embedMsgId = sentEmbedMsg.id
        return sentEmbedMsg

    def countVote(self):
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
        return retDict
