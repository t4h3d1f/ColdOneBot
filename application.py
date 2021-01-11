import discord
import asyncio
import logging
import os
import traceback
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext import commands
import pymysql.cursors
from random import randint
from bisect import bisect_right
import threading

# Customs
from ColdOneCore import CoreColors, getConnection
from Bet import Bet
from Vote import Vote
from JokeGetter import JokeGetter
from Vote import Vote
from EventHandlers.ReactionHandler import ReactionHandler
from Roll import Roll

botPrefix = "&"
bot = commands.Bot(command_prefix=botPrefix)
pogUrl = "https://img2.123clipartpng.com/poggers-transparent-picture-2101472-poggers-transparent-poggers-emote-transparent-clipart-300_300.png"

# probability a track will play (1-1000) and the track name
tracks = [
    (750, 'yooo.m4a'),
    (990, 'YOOOOOOOOOOOUUUUUUU (152kbit_AAC).m4a'),
    (1000, 'Discord Message Sounds.m4a')
]

memeTracks = [
    'Discord Message Sound.m4a',
    'A True Meme War Veteran.m4a',
    'accidentally start a endgame boss fight.m4a',
    'Are you sober now.m4a',
    'beating my damn dick.m4a',
    'Bruh.m4a',
    'CHOCOLATE.m4a',
    'Do I look like I know what a JPEG is.m4a',
    'GameCube intro.m4a',
    'hardcore hacking mode.m4a',
    'insert drive.m4a',
    'Morrowind.m4a',
    'Omae Wa Mou Shindeiru.m4a',
    'Poisoned.m4a',
    'Tell Me Does He Look Like a BITCH.m4a',
    'What is the airspeed velocity of an unladen swallow.m4a'
]

# global variables
memer = None
memeThread = None
server = None

class Timer:
    def __init__(self, min_interval, max_interval, callback):
        self._callback = callback
        self._min_interval = min_interval
        self._max_interval = max_interval
        self._task = asyncio.ensure_future(self._job())
        self._running = True
        print('timer initialized')

    async def _job(self):
        playlist = [randint(0, len(memeTracks)-1) for i in range(len(memeTracks))]
        playlistIdx = 0
        while self._running:
            sleepTime = randint(self._min_interval, self._max_interval)
            print('sleeping for {0}'.format(sleepTime))
            await asyncio.sleep(sleepTime)
            print('proc-d')
            await self._callback(playlist[playlistIdx])
            playlistIdx = playlistIdx + 1
            if (playlistIdx >= len(playlist)):
                self._task.cancel()

    def is_alive(self):
        return self._running

    def cancel(self):
        self._running = False
        self._task.cancel()

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if "durag" in message.content:
        if "&durag" not in message.content:
            if not message.author.bot:
                print(message)
                sql = "INSERT INTO durag (durag_time, username) VALUES (%s,%s)"
                vals = (message.created_at, message.author.name)
                mydb = getConnection()
                mycursor = mydb.cursor()
                mycursor.execute(sql, vals)
                mydb.commit()
                mydb.close()

@bot.command(name="coco", help="Crack open a cold one with the boys")
async def coco(ctx):
    message = ctx.message
    print(message)
    sql = "INSERT INTO coldOnes (time, username) VALUES (%s,%s)"
    vals = (message.created_at, message.author.name)
    mydb = getConnection()
    mycursor = mydb.cursor()
    mycursor.execute(sql, vals)
    mydb.commit()
    mycursor.execute("SELECT COUNT(*) FROM coldOnes")
    myresult = mycursor.fetchall()
    chance = randint(1, 100)
    if chance > 90:
        await message.channel.send("I'm gnot a gnelf, I'm gnot a gnoblin, I'm a gnome, and you've been GNOMED!".format(myresult[0][0]))
    else:
        await message.channel.send("Nice! {0} cold ones have been opened!".format(myresult[0][0]))

    if message.author.name == "Adventure_Tom":
        emoji = get(bot.emojis, name='Maybe')
        await message.add_reaction(emoji)
    if message.author.name == "Captain Crayfish":
        emoji = get(bot.emojis, name='Wooo')
        await message.add_reaction(emoji)
    if not message.author.voice:
        mydb.close()
        return
    channel = message.author.voice.channel
    if not channel:
        mydb.close()
        return
    await channel.connect()
    # Generate a number between 1 and 1000
    audiochance = randint(1, 1000)
    # figure out what track this corrisponds to
    index = bisect_right(tracks, (audiochance, ''))
    source = FFmpegPCMAudio(tracks[index][1])
    ctx.voice_client.play(source)
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    await ctx.voice_client.disconnect()
    mydb.close()

# Start monitoring for user in voice channel.
# once enabled will join voice chat after a random amount of time
# and play a meme audio clip.
# continues until manually disabled with "nofunnybusiness" or
# user leaves voice chat.
@bot.command(name="automeme", help="Automatic meming (☞⌐▀͡ ͜ʖ͡▀ )☞")
async def automeme_enable(message):
    global memer
    memer = message.author
    global server
    server = message.guild
    print(memer)
    global memeThread
    memeThread = Timer(180, 900, blast_meme)

# Stop memeThread and clear original user from memory
@bot.command(name="nofunnybusiness", help="Disables automeme")
async def automeme_disable(message):
    if memeThread is not None:
        if memeThread.is_alive():
            memeThread.cancel()
            global memer
            memer = None

@bot.command(name="stats", help="View your drinking stats")
async def stats(message):
    mydb = getConnection()
    mycursor = mydb.cursor()
    mycursor.execute('select COUNT(*) from coldOnes where username = %s;',
                     (message.author.name,))
    result = mycursor.fetchall()
    print(result[0][0])
    await message.channel.send("{0} has recorded {1} cold ones opened!".format(
                                message.author.name, result[0][0]))
    if result[0][0] > 100:
        await message.channel.send('you alcholholic')
    mydb.close()

async def blast_meme(idx):
    userid = memer.id
    print(id)
    user = bot.get_user(userid)
    print(user)
    member = server.get_member(user.id)
    print(member.nick)
    print(member.voice.channel)
    print(member.voice.channel.id)
    channel = bot.get_channel(member.voice.channel.id)
    if not channel:
        memeThread.cancel()
        return
    if memer not in channel.members:
        memeThread.cancel()
        return
    await channel.connect()
    source = FFmpegPCMAudio(memeTracks[idx])
    server.voice_client.play(source)
    while server.voice_client.is_playing():
        await asyncio.sleep(1)
    await server.voice_client.disconnect()

@bot.command(name="leaderboard",
             help="View the current drinking leaders of the server")
async def leaderboard(message):
    mydb = getConnection()
    mycursor = mydb.cursor()
    mycursor.execute('SELECT username from coldOnes GROUP BY username ORDER BY COUNT(*) DESC LIMIT 5;')
    result = mycursor.fetchall()
    response = ""
    place = 1
    print(result)
    for name in result:
        mycursor.execute('SELECT COUNT(*) from coldOnes where username=%s',
                         (name[0],))
        freq = mycursor.fetchall()
        response += "{0}. {1} with {2} cold one{3} opened!\r\n".format(
                    place, name[0], freq[0][0], '' if freq[0][0] == 1 else "s")
        place += 1
    await message.channel.send(response)
    mydb.close()

@bot.command(name="ohno", help="Try and and find out")
async def ohno(message):
    channel = message.author.voice.channel
    if not channel:
        return
    await channel.connect()
    source = FFmpegPCMAudio('Sad Trombone.m4a')
    player = message.voice_client.play(source)
    while message.voice_client.is_playing():
        await asyncio.sleep(1)
    await message.voice_client.disconnect()

@bot.command(name="durag", help="Would you tell me the truth?")
async def durag(message):
    mydb = getConnection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM durag")
    myresult = mycursor.fetchall()
    await message.channel.send("How do I look in my {0} durag(s)?".format(
        myresult[0][0]))
    mydb.close()

# Vote Shit

# Parses if this is vote creation or closure
@bot.command(name="vote", help="Call a vote, exercise your civic right")
async def parseVote(ctx):
    cmdBase = botPrefix + "vote "
    author = ctx.author.name
    message = ctx.message.content[len(cmdBase):]
    if Vote.doesUserVoteExist(author):
        await Vote.closeVote(ctx, Vote.popVote(author))
    else:
        await Vote.createVote(ctx, author, message)

# Joke Shit

# Gets and sends out a random joke
@bot.command(name="joke", help="Get me a joke :pog:")
async def getMeAJokeBaby(ctx):
    await ctx.channel.send(embed=JokeGetter.getEmbed())

# Bet Shit

# Bot command, displays the current pogs standings
@bot.command(name="pogs", help="Show pogs baby")
async def showPogs(ctx):
    retVals = Bet.selectAllPogs()
    embed = discord.Embed(color=CoreColors.LeaderboardColor, title="Pog Leaderboard")
    embed.set_thumbnail(url=pogUrl)
    for row in retVals:
        embed.add_field(name=row[2], value=row[3], inline=True)
    print("Pogs: " + str(retVals))
    channel = ctx.message.channel
    await channel.send(embed=embed)

# Bot command, reads the message, and creates or close out the bet
@bot.command(name="bet", help="Bet pogs baby")
async def parseBet(ctx):
    cmdBase = botPrefix + "bet "
    author = ctx.author.name
    message = ctx.message.content[len(cmdBase):]
    if Bet.doesUserBetExist(author):
        await Bet.closeBet(ctx, Bet.popBet(author), message)
    else:
        await Bet.createBet(ctx, author, message)

@bot.command(name="fIxThEsEmOnEy", help="fix the money, gotta be on a special spot tho")
async def fixMoney(ctx):
    guild = ctx.guild
    print(guild.channels)
    if len(guild.channels) > 4:
        print("bail on fIxThEsEmOnEy")
        return
    db = getConnection()
    mycursor = db.cursor()
    mycursor.execute("UPDATE pogs SET pogs = 1000")
    db.commit()

@bot.command(name="roll", help="Roll a die (&roll d<1-1000>")
async def rollDie(ctx):
    cmdBase = botPrefix + "roll "
    message = ctx.message.content[len(cmdBase):]
    ctx.message.channel.send(await Roll.roll(message))

@bot.event
async def on_reaction_add(reaction, user):
    ReactionHandler.checkForMessage(reaction, user)

def main():
    try:
        while(True):
            print('hello')
            bot.run(os.environ.get('DISCORD_TOKEN'))
            bot.logout()
    except Exception as e:
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()
