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



#        if message.content.startswith('crack open a cold one'):
#            sql = "INSERT INTO coldOnes (time, username) VALUES (%s,%s)"
#            vals = (message.created_at, message.author.name)
#            mycursor.execute(sql,vals)
#            mydb.commit()
#            mycursor.execute("SELECT COUNT(*) FROM coldOnes")
#            myresult = mycursor.fetchall()
#            await message.channel.send("Nice! {0} cold ones have been opened!".format(myresult[0][0]))


bot = commands.Bot(command_prefix="&")

# probability a track will play (1-1000) and the track name

tracks = [
    (750, 'yooo.m4a'),
    (990, 'YOOOOOOOOOOOUUUUUUU (152kbit_AAC).m4a'),
    (1000, 'Discord Message Sounds.m4a')
]


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
    index = bisect_right(tracks, audiochance)
    source = FFmpegPCMAudio(tracks[index][1])
    ctx.voice_client.play(source)
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    await ctx.voice_client.disconnect()
    mydb.close()


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
