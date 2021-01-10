import discord

from ColdOneCore import CoreColors
from VoteBase import VoteBase
from Discord.HasAddReactCallback import HasAddReactCallback
from EventHandlers.ReactionHandler import ReactionHandler

pogUrl = "https://img2.123clipartpng.com/poggers-transparent-picture-2101472-poggers-transparent-poggers-emote-transparent-clipart-300_300.png"
defaultAmount = 50

class Bet(VoteBase, HasAddReactCallback):

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

    # Verifies that each user involved in the bet exists in the user table
    @staticmethod
    def checkUsersExist(payout, myCursor, db):
        usersToCheck = payout['winners'] + payout['losers']
        usersToAdd = []
        getAllSql = "SELECT discord_user_id FROM pogs;"
        insertSql = "INSERT INTO pogs(discord_user_id, username, pogs) VALUES (%s, %s, %s);"
        myCursor.execute(getAllSql)
        getAllRet = myCursor.fetchall()
        for curUser in usersToCheck:
            tuple = (str(curUser.id),)
            if not tuple in getAllRet:
                # add user
                insertVals = (str(curUser.id), str(curUser.name), 1000)
                myCursor.execute(insertSql, insertVals)
                db.commit()

    # Updates pog table with winner and loser amounts
    @staticmethod
    def updateUserPogs(payout, myCursor, db):
        if ((not payout['winners']) and (not payout['losers'])):
            return
        # If winners exist, update them
        if len(payout['winners']):
            sqlUpdateQuery = "UPDATE pogs SET pogs = pogs + " + str(payout['winAmount'])
            sqlUpdateQuery += "\nWHERE discord_user_id = "
            sqlAdd = " OR discord_user_id = "
            for curWinner in payout['winners']:
                sqlUpdateQuery += str(curWinner.id) + "\n" + sqlAdd
            sqlUpdateQuery = sqlUpdateQuery[:len(sqlUpdateQuery) - len(sqlAdd)]
            myCursor.execute(sqlUpdateQuery)
            db.commit()
        # If losers exist, update them too
        if len(payout['losers']):
            sqlUpdateQuery = "UPDATE pogs SET pogs = pogs - " + str(payout['loseAmount'])
            sqlUpdateQuery += "\nWHERE discord_user_id = "
            sqlAdd = " OR discord_user_id = "
            for curLoser in payout['losers']:
                sqlUpdateQuery += str(curLoser.id) + "\n" + sqlAdd
            sqlUpdateQuery = sqlUpdateQuery[:len(sqlUpdateQuery) - len(sqlAdd)]
            myCursor.execute(sqlUpdateQuery)
            db.commit()

    # Returns all rows from pogs
    @staticmethod
    def selectAllPogs(db):
        myCursor = db.cursor()
        sql = "SELECT * FROM pogs ORDER BY pogs DESC;"
        myCursor.execute(sql)
        return myCursor.fetchall()

    # Prints out all pogs to python output
    @staticmethod
    def selectAndPrintAll():
        print("All pogs: ")
        rows = Bet.selectAllPogs()
        for row in rows:
            print(f'id:{row[0]} disc_id:{row[1]} user:{row[2]} pogs:{row[3]}')

    # Closes down a bet
    #
    # TODO: Edit or delete old embed from bet creation
    @staticmethod
    async def closeBet(ctx, db, bet, message):
        if not bet:
            return
        forsWin = message.find("win") != -1
        payouts = bet.calculatePayouts(forsWin)
        print("Payout: " + str(payouts))
        myCursor = db.cursor()
        Bet.checkUsersExist(payouts, myCursor, db)
        Bet.updateUserPogs(payouts, myCursor, db)
        await bet.clearEmbed()
        await bet.getCloseEmbed(ctx, payouts)
        return

    # Sets up a bet, format being &bet
    # Ex: &bet I'm gonna beat your ass in TFT
    # Ex: &bet 25, You'll laugh before me
    @staticmethod
    async def createBet(ctx, author, message):
        amount = defaultAmount
        description = "";
        msgSplit = message.split(", ")
        if len(msgSplit) > 1:
            amount = int(msgSplit[0].strip())
            description = msgSplit[1]
        else:
            description = msgSplit[0]
        bet = Bet(author, amount, description)
        await bet.sendEmbed(ctx)
        ReactionHandler.listenOnMessage(bet)

    # Constructor, checks if the author has a bet and if not, adds to bets
    def __init__(self, author, amount = 50, desc = ""):
        # Only one bet per user is allowed
        if Bet.doesUserBetExist(author):
            return null
        self.amount = amount
        self.author = author
        self.betDesc = desc
        self.voteFor = []
        self.voteAgainst = []

        title = "Poggy bet"
        embedDescription = "The bet amount is " + str(self.amount) + " pogs."
        if len(desc) > 0:
            title += ": " + desc
        footer = "Bet with them with +1, or against them with -1. End the bet by typing &bet, followed by win or lose."
        HasAddReactCallback.__init__(self);
        VoteBase.__init__(
            self,
            title=title,
            author=self.author,
            desc=embedDescription,
            footer=footer,
            color=CoreColors.InteractColor,
            thumbnail=pogUrl)
        Bet.activeBets.update({self.author:self})

    # Callback called when a react is added to this object's discord message.
    def addReactCallback(self, react: discord.Reaction, user: discord.User):
        if (user in self.voteFor) or (user in self.voteAgainst):
            return
        if react.emoji == "👍":
            self.voteFor.append(user)
        if react.emoji == "👎":
            self.voteAgainst.append(user)

    # Calculates the payouts for the winners and losers.
    def calculatePayouts(self, forsWin = True):
        countWinners = 0
        countLosers = 0
        winUsers = []
        loseUsers = []
        if forsWin:
            countWinners = len(self.voteFor)
            countLosers = len(self.voteAgainst)
            winUsers = self.voteFor
            loseUsers = self.voteAgainst
        else:
            countWinners = len(self.voteAgainst)
            countLosers = len(self.voteFor)
            winUsers = self.voteAgainst
            loseUsers = self.voteFor

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

    async def getCloseEmbed(self, ctx, payout):
        self.setFooter("")
        self.setTitle("Bet over: " + self.betDesc)
        descStr = "Winners get " + str(payout.get('winAmount')) + ". "
        descStr += "Losers lose " + str(payout.get('loseAmount')) + "."
        self.setDescription(descStr)
        await self.sendEmbed(ctx, True)
