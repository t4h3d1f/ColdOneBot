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

    # Returns all rows from pogs
    @staticmethod
    def selectAllPogs(db):
        myCursor = db.cursor()
        sql = "SELECT * FROM pogs ORDER BY pogs DESC;"
        myCursor.execute(sql)
        return myCursor.fetchall()

    # Prints out all pogs to python output
    @staticmethod
    def selectAndPrintAll(db):
        print("All pogs: ")
        rows = selectAllPogs()
        for row in rows:
            print(f'id:{row[0]} disc_id:{row[1]} user:{row[2]} pogs:{row[3]}')

    # Updates pog table with winner and loser amounts
    @staticmethod
    def updateUserPogs(payout, myCursor, db):
        if ((not payout['winners']) or (not payout['losers'])):
            return

        sqlUpdateQuery = "";
        for curWinner in payout['winners']:
            sqlUpdateQuery += "UPDATE pogs SET pogs = pogs + " + str(payout['winAmount'])
            sqlUpdateQuery += " WHERE discord_user_id = " + str(curWinner.id) + "\n"
        for curLoser in payout['losers']:
            sqlUpdateQuery += "UPDATE pogs SET pogs = pogs - " + str(payout['loseAmount'])
            sqlUpdateQuery += " WHERE discord_user_id = " + str(curLoser.id) + "\n"
        sqlUpdateQuery += ";"
        if sqlUpdateQuery:
            myCursor.execute(sqlUpdateQuery)
            db.commit()

    # Verifies that each user involved in the bet exists in the user table
    @staticmethod
    def checkUsersExist(payout, myCursor, db):
        usersToCheck = payout['winners'] + payout['losers']
        usersToAdd = []
        getAllSql = "SELECT discord_user_id FROM pogs;"
        insertSql = "INSERT INTO pogs(discord_user_id, username, pogs) VALUES (%s, %s, %s);"
        myCursor.execute(getAllSql)
        getAllRet = myCursor.fetchall()
        print(str(getAllRet))
        for curUser in usersToCheck:
            tuple = (str(curUser.id),)
            if not tuple in getAllRet:
                # add user
                insertVals = (str(curUser.id), str(curUser.name), 1000)
                myCursor.execute(insertSql, insertVals)
                db.commit()

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
