import discord
import datetime
import asyncio
import logging
import os
import traceback
import threading
import DiscordUtils
from discord.embeds import Embed
from discord.enums import ContentFilter
from discord.ext.commands.core import has_guild_permissions
from discord.ext.commands.help import Paginator
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, ComponentContext
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.model import ButtonStyle
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ext import commands

from random import randint
from bisect import bisect_right
import threading
import sqlite3 as sl

# Customs
from ColdOneCore import CoreColors
from Bet import Bet
from Vote import Vote
from JokeGetter import JokeGetter
from Vote import Vote
from EventHandlers.ReactionHandler import ReactionHandler
from Roll import Roll
from Poll import Poll
from Audio import Audio
from Dinner import Dinner


botPrefix = "&"
bot = commands.Bot(command_prefix=botPrefix)
pogUrl = "https://img2.123clipartpng.com/poggers-transparent-picture-2101472-poggers-transparent-poggers-emote-transparent-clipart-300_300.png"

client = discord.Client(intents=discord.Intents.default())
slash = SlashCommand(client, sync_commands=True)

# put server id here
guild_ids = []

con = sl.connect('coldone.db')

musicTread = DiscordUtils.Music()


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


# interactive stuff


class Timer:
    def __init__(self, min_interval, max_interval, callback):
        self._callback = callback
        self._min_interval = min_interval
        self._max_interval = max_interval
        self._task = asyncio.ensure_future(self._job())
        self._running = True
        print('timer initialized')

    async def _job(self):
        playlist = [randint(0, len(memeTracks)-1)
                    for i in range(len(memeTracks))]
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


@slash.slash(name='coco', description="Crack open a cold one with the boys",
             guild_ids=guild_ids)
async def coco(ctx):
    with con:
        con.execute(f'INSERT INTO coldOnes (time, username) VALUES (?,?);',
                    (datetime.datetime.now(), ctx.author.id))
        cursor = con.execute("SELECT COUNT(*) FROM coldOnes")
        myresult = cursor.fetchall()
    chance = randint(1, 100)
    if chance > 90:
        await ctx.send("I'm gnot a gnelf, I'm gnot a gnoblin, I'm a gnome, and you've been GNOMED!".format(myresult[0][0]), hidden=True)
    else:
        await ctx.send(f"Nice! {myresult[0][0]} cold ones have been opened!", hidden=True)
    if not ctx.author.voice:
        return
    channel = ctx.author.voice.channel
    if not channel:
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


# Start monitoring for user in voice channel.
# once enabled will join voice chat after a random amount of time
# and play a meme audio clip.
# continues until manually disabled with "nofunnybusiness" or
# user leaves voice chat.


@slash.slash(name="automeme", description="Automatic meming (☞⌐▀͡ ͜ʖ͡▀ )☞",
             guild_ids=guild_ids)
async def automeme_enable(message):
    global memer
    memer = message.author
    global server
    server = message.guild
    global memeThread
    memeThread = Timer(180, 900, blast_meme)

# Stop memeThread and clear original user from memory


@slash.slash(name="nofunnybusiness", description="Disables automeme",
             guild_ids=guild_ids)
async def automeme_disable(message):
    if memeThread is not None:
        if memeThread.is_alive():
            memeThread.cancel()
            global memer
            memer = None


@slash.slash(name="stats", description="View your drinking stats",
             guild_ids=guild_ids)
async def stats(message):
    cursor = con.execute('select COUNT(*) from coldOnes where username = ?;',
                         (message.author.id,))
    result = cursor.fetchall()
    await message.send("{0} has recorded {1} cold ones opened!".format(
        message.author.name, result[0][0]))


async def blast_meme(idx):
    userid = memer.id
    user = bot.get_user(userid)
    member = server.get_member(user.id)
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


@slash.slash(name="leaderboard",
             description="View the current drinking leaders of the server",
             guild_ids=guild_ids)
async def leaderboard(message):
    cursor = con.execute(
        'SELECT username from coldOnes GROUP BY username ORDER BY COUNT(*) DESC LIMIT 5;')
    result = cursor.fetchall()
    response = ""
    for place, id in enumerate(result):
        cursor = con.execute('SELECT COUNT(*) from coldOnes where username=?',
                             (id[0],))
        freq = cursor.fetchall()
        user = client.get_user(int(id[0]))
        response += "{0}. {1} with {2} cold one{3} opened!\r\n".format(
                    place, user.name, freq[0][0], '' if freq[0][0] == 1 else "s")
    await message.send(response)


@slash.slash(name="durag", description="Would you tell me the truth?",
             guild_ids=guild_ids)
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


@slash.slash(name="vote", description="Call a vote, exercise your civic right",
             guild_ids=guild_ids)
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


@slash.slash(name="joke", description="Get me a joke :pog:",
             guild_ids=guild_ids)
async def getMeAJokeBaby(ctx):
    await ctx.channel.send(embed=JokeGetter.getEmbed())

# Bet Shit

# Bot command, displays the current pogs standings


@slash.slash(name="pogs", description="Show pogs baby",
             guild_ids=guild_ids)
async def showPogs(ctx):
    retVals = Bet.selectAllPogs(con)
    embed = discord.Embed(
        color=CoreColors.LeaderboardColor, title="Pog Leaderboard")
    embed.set_thumbnail(url=pogUrl)
    for row in retVals:
        embed.add_field(name=row[2], value=row[3], inline=True)
    print("Pogs: " + str(retVals))
    channel = ctx.message.channel
    await channel.send(embed=embed)

# Bot command, reads the message, and creates or close out the bet


@slash.slash(name="bet", description="Bet pogs baby",
             guild_ids=guild_ids)
async def parseBet(ctx):
    cmdBase = botPrefix + "bet "
    author = ctx.author.name
    message = ctx.message.content[len(cmdBase):]
    if Bet.doesUserBetExist(author, con):
        await Bet.closeBet(ctx, Bet.popBet(author), message)
    else:
        await Bet.createBet(ctx, author, message)

# Poll Shit


@slash.slash(name="poll", description="Start a poll! Know which game to play next",
             guild_ids=guild_ids)
async def parsePoll(ctx):
    await Poll.createPoll(ctx, bot)


@slash.slash(name="fIxThEsEmOnEy", description="fix the money, gotta be on a special spot tho",
             guild_ids=guild_ids)
async def fixMoney(ctx):
    guild = ctx.guild
    print(guild.channels)
    if len(guild.channels) > 4:
        print("bail on fIxThEsEmOnEy")
        return

    con.execute("UPDATE pogs SET pogs = 1000")


@slash.slash(name="roll", description="Roll a die",
             options=[
                 create_option(
                     name='d',
                     description='number of sides on the die',
                     option_type=4,
                     required=True
                 )
             ],
             guild_ids=guild_ids)
async def rollDie(ctx, d: int):
    # cmdBase = botPrefix + "roll "
    # message = ctx.message.content[len(cmdBase):]
    await ctx.send(await Roll.roll(d))


@slash.slash(name='MusicBot', description='Open the music control panel', guild_ids=guild_ids)
async def buttons(ctx):
    buttons = [
        create_button(
            style=ButtonStyle.green,
            label='▶',
            custom_id='resume'
        ),
        create_button(
            style=ButtonStyle.blue,
            label='⏸',
            custom_id='pause'
        ),
        create_button(
            style=ButtonStyle.red,
            label='⏹',
            custom_id='stop'
        ),
        create_button(
            style=ButtonStyle.blue,
            label='⏭',
            custom_id='skip'
        ),
        create_button(
            style=ButtonStyle.gray,
            label='📃',
            custom_id='queue'
        )
    ]
    action_row = create_actionrow(*buttons)
    await ctx.send('Now playing...', components=[action_row])


# @slash.slash(name='play', description='Plays the attached song. Use the -dank argument for memes [̲̅$̲̅(̲̅ ✧≖ ͜ʖ≖)̲̅$̲̅]',
#              guild_ids=guild_ids)
# async def play(ctx):
#     await Audio.playSong(ctx)


@slash.slash(name='dj', description='Add the bot to the current voice channel', guild_ids=guild_ids)
async def join(ctx):
    await ctx.author.voice.channel.connect()
    await ctx.send('connected to voice',  hidden=True)


@slash.slash(name='dj_disconnect', description='disconnect bot from voice', guild_ids=guild_ids)
async def disconnect(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send('disconnected from voice', hidden=True)


@slash.slash(name='Play',
             options=[
                 create_option(
                     name='url',
                     description='youtube url',
                     option_type=3,
                     required=True
                 )
             ],
             guild_ids=guild_ids)
async def play(ctx, url):

    player = musicTread.get_player(guild_id=ctx.guild.id)
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    if not player:
        player = musicTread.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await ctx.defer(hidden=True)
        await player.queue(url, search=True)
        song = await player.play()

        await ctx.send(f"Playing {song.name}", hidden=True)
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"Queued {song.name}", hidden=True)
        # insert record
    with con:
        con.execute(
            f'INSERT INTO MUSIC(url,title,user,date) values(?,?,?,?);',
            (url, song.name, ctx.author.id, datetime.datetime.now()))


@ slash.component_callback()
async def pause(ctx: ComponentContext):
    player = musicTread.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.edit_origin(content='Paused')


@ slash.component_callback()
async def resume(ctx: ComponentContext):
    player = musicTread.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.edit_origin(content='Resuming')


@ slash.component_callback()
async def stop(ctx: ComponentContext):
    player = musicTread.get_player(guild_id=ctx.guild.id)
    await player.stop()
    await ctx.voice_client.disconnect()
    await ctx.edit_origin(content="Stopped")


@ slash.component_callback()
async def skip(ctx: ComponentContext):
    player = musicTread.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    if len(data) == 2:
        await ctx.edit_origin(content=f"Skipped from {data[0].name} to {data[1].name}")
    else:
        await ctx.edit_origin(content=f"Skipped {data[0].name}")


@ slash.component_callback()
async def queue(ctx: ComponentContext):
    player = musicTread.get_player(guild_id=ctx.guild.id)
    queueMsg = ''
    for song in player.current_queue():
        queueMsg += song.name+'\n'
    embed = discord.Embed(color=ctx.author.color).add_field(
        name='Current Queue', value=queueMsg)
    await ctx.send(embed=embed)
# @bot.event
# async def on_reaction_add(reaction, user):
#     ReactionHandler.checkForMessage(reaction, user)

# def main():
#     try:
#         while(True):
#             print('hello')
#             bot.run(os.environ.get('DISCORD_TOKEN'))
#             bot.logout()
#     except Exception as e:
#         logging.error(traceback.format_exc())


@bot.command(name="dinner", help="Tells you what to get for dinner")
async def rollDie(ctx):
    await ctx.message.channel.send(await Dinner.dinner())


@ client.event
async def on_ready():
    print('online')


client.run(os.environ.get('DISCORD_TOKEN'))

# if __name__ == "__main__":
#     main()
