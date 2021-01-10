import discord

# Interface defining a data model with a discord message.
class HasMessage:

    def getChannel(self):
        return self.channel

    def setChannel(self, channel: discord.TextChannel):
        self.channel = channel

    def getMessageId(self):
        return self.messageId

    def setMessageId(self, id):
        self.messageId = id

    async def getMessage(self):
        if self.getMessageId():
            return await self.getChannel().fetch_message(self.getMessageId())
