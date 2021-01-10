import discord

from Discord.HasAddReactCallback import HasAddReactCallback

# Handles receiving and callbacks for messages listening for reacts.
class ReactionHandler:

    reactListeners = []

    # Adds a message to the dictionary of messages being listened for.
    @staticmethod
    def listenOnMessage(cbObject: HasAddReactCallback):
        ReactionHandler.reactListeners.append(cbObject)

    # Called whenever a react is added, checks if the message the react was
    # added to is in the watch list, and if so calls the callback with the
    # react.
    @staticmethod
    def checkForMessage(react: discord.Reaction, user: discord.User):
        for listener in ReactionHandler.reactListeners:
            if listener.isMatch(react, user):
                listener.addReactCallback(react, user)

    @staticmethod
    def removeListener(cbObject: HasAddReactCallback):
        ReactionHandler.reactListeners.remove(cbObject)
