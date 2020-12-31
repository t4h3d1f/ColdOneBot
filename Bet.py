import discord
from ColdOneCore import CoreColors

pogUrl = "https://img2.123clipartpng.com/poggers-transparent-picture-2101472-poggers-transparent-poggers-emote-transparent-clipart-300_300.png"

class Bet:

    activeBets = {}

    # Checks if a user already has a bet going
    @staticmethod
    def doesUserBetExist(author):
        return author in Bet.activeBets

    # Removes and returns a user's bet
    @staticmethod
    def popBet(author):
        bet = Bet.activeBets[author]
        del Bet.activeBets[author]
        return bet

    # Constructor, checks if the author has a bet and if not, adds to bets
    def __init__(self, author, amount = 50, desc = ""):
        if Bet.doesUserBetExist(author):
            return null
        self.amount = amount
        self.author = author

        self.embedTitle = "Poggy bet"
        self.embedAuthor = self.author
        self.embedDescription = "The bet amount is " + str(self.amount) + " pogs."
        if len(desc) > 0:
            self.embedTitle += ": " + desc
        self.embedFooter = "Bet with them with +1, or against them with -1."
        self.embedFooter += " End the bet by typing &bet, followed by win or lose."
        Bet.activeBets.update({self.author:self})

    # Creates the embed object for this bet
    def getEmbed(self):
        self.embed = discord.Embed(color=CoreColors.InteractColor, title=self.embedTitle, description=self.embedDescription)
        self.embed.set_author(name=self.embedAuthor)
        self.embed.set_footer(text=self.embedFooter)
        self.embed.set_thumbnail(url=pogUrl)
        return self.embed

    # Calculates the payouts for the winners and losers
    async def calculatePayouts(self, forsWin = True):
        usersFor = []
        usersAgainst = []
        msg = await self.channel.fetch_message(self.embedMsgId)
        # Count of the reactions
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

        countWinners = 0
        countLosers = 0
        winUsers = []
        loseUsers = []
        if forsWin:
            countWinners = len(usersFor)
            countLosers = len(usersAgainst)
            winUsers = usersFor
            loseUsers = usersAgainst
        else:
            countWinners = len(usersAgainst);
            countLosers = len(usersFor)
            winUsers = usersAgainst
            loseUsers = usersFor

        # Validate users lists. Anyone who bets twice loses
        for user in loseUsers:
            if user in winUsers:
                winUsers.remove(user)

        retDict = {};
        retDict['winAmount'] = 0 if countWinners < 1 else int((self.amount * countLosers) / countWinners)
        retDict['loseAmount'] = self.amount
        retDict['winners'] = winUsers
        retDict['losers'] = loseUsers
        return retDict
