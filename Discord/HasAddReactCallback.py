import discord

from Discord.HasMessage import HasMessage

# "Interface" for handling add react callbacks.
class HasAddReactCallback(HasMessage):

    def __init__(self, allowReactsFromBots = False):
        self.setAllowReactsFromBots(allowReactsFromBots)

    # Callback for when a react is added to the message made by this data model.
    def addReactCallback(self, react: discord.Reaction, user: discord.User):
        pass

    # Checks if the given react has a message that matches this callback.
    def isMatch(self, react: discord.Reaction, user: discord.User):
        # False if the user reacting is a bot and that's disabled
        if user.bot and not self.allowReactsFromBots:
            return False

        if react.message.id == self.getMessageId():
            return True
        return False

    def setAllowReactsFromBots(self, allow):
        self.allowReactsFromBots = allow
