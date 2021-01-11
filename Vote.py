import discord
from ColdOneCore import CoreColors
from VoteBase import VoteBase

class Vote(VoteBase):

    activeVotes = {}

    # Checks if a user already has a vote going
    @staticmethod
    def doesUserVoteExist(author):
        return author in Vote.activeVotes

    # Removes and returns a user's bet
    @staticmethod
    def popVote(author):
        vote = Vote.activeVotes[author]
        del Vote.activeVotes[author]
        return vote

    # Creates a vote and sends its embed
    @staticmethod
    async def createVote(ctx, author, message):
<<<<<<< HEAD
        if (not author) or (not message):
            return
=======
>>>>>>> master
        vote = Vote(author=author, description=message)
        await vote.sendEmbed(ctx)

    @staticmethod
<<<<<<< HEAD
    async def closeVote(ctx, vote):
        if not vote:
            return
        await vote._closeVote(ctx)
=======
    async def closeVote(vote):
        if not vote:
            return
        await vote._closeVote()
>>>>>>> master

    def __init__(self, author, description):
        self.author = author
        self.voteDesc = description
        super().__init__(title=description, author=author, color=CoreColors.InteractColor)
        Vote.activeVotes.update({self.author:self})

<<<<<<< HEAD
    async def _closeVote(self, ctx):
        tally = await self.countVote()
        await self.clearEmbed()
        await self.getCloseEmbed(ctx, tally)

    async def getCloseEmbed(self, ctx, tally):
        ayesHaveIt = len(tally.get('voteFor')) - len(tally.get('voteAgainst'))
        super().setTitle("Vote over: " + self.voteDesc)
        if ayesHaveIt > 0:
            super().setDescription("Ayes have it!")
        elif ayesHaveIt < 0:
            super().setDescription("Nays have it!")
        else:
            super().setDescription("The vote's a tie!")
        await self.sendEmbed(ctx, True)
=======
    async def _closeVote(self):
        tally = await self.countVote()
        await self.clearEmbed()
        await self.getCloseEmbed(tally)

    async def getCloseEmbed(self, tally):
        ayesHaveIt = len(tally.get('voteFor')) > len(tally.get('voteAgainst'))

        self.embed = None
        self.embedTitle = "Vote over: " + self.voteDesc
        self.embedDescription = "Ayes have it!" if ayesHaveIt else "Nays have it!"
        await self.channel.send(embed=self.getEmbed())
>>>>>>> master
