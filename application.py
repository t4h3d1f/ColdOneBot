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

bot = commands.Bot(command_prefix="&")

# probability a track will play (1-1000) and the track name
tracks = [
    (750, 'yooo.m4a'),
    (990, 'YOOOOOOOOOOOUUUUUUU (152kbit_AAC).m4a'),
    (1000, 'Discord Message Sounds.m4a')
]

memeTracks = [
    'Discord Message Sounds.m4a',
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
    'Potion Seller.m4a',
    'Tell Me Does He Look Like a BITCH.m4a',
    'What is the airspeed velocity of an unladen swallow.m4a'
]

# global variables
memer = None
memeThread = None


class Timer:
    def __init__(self, min_interval, max_interval, callback):
        self._callback = callback
        self._min_interval = min_interval
        self._max_interval = max_interval
        self._task = asyncio.ensure_future(self._job())
        print('timer initialized')

    async def _job(self):
        await asyncio.sleep(randint(self._min_interval, self._max_interval))
        print('proc-d')
        await self._callback()

    def cancel(self):
        self._task.cancel()


def getConnection():
    mydb = pymysql.connect(
        host=os.environ.get("SQL_HOST"),
        port=3306,
        db=os.environ.get("SQL_DB"),
        user=os.environ.get("SQL_USER"),
        password=os.environ.get("SQL_PASSWORD")
    )
    return mydb


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
    print(memer)
    global memeThread
    memeThread = Timer(15, 60, blast_meme)


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


async def blast_meme():
    userid = memer.id
    print(id)
    user = bot.get_user(userid)
    print(user)
    print(user.voice.channel)
    print(user.voice.channel.id)
    channel = bot.get_channel(user.voice.channel.id)
    if not channel:
        memeThread.cancel()
        return
    if memer not in channel.members:
        memeThread.cancel()
        return
    await channel.connect()
    # Pick a random track
    idx = randint(0, len(memeTracks)-1)
    source = FFmpegPCMAudio(memeTracks[idx])
    ctx.voice_client.play(source)
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    await ctx.voice_client.disconnect()


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
