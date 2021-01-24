import discord
import os
import asyncio
from pydub import AudioSegment
from pydub.playback import play
from discord import FFmpegPCMAudio


class Audio:
    async def playSong(ctx):
        message = ctx.message
        if len(message.attachments) == 0:
            await message.channel.send('attach a file first')
            return
        fname = message.attachments[0].filename
        try:
            await message.attachments[0].save(fname)
        except discord.NotFound:
            return
        # fry the shit out of this song
        if message.content.__contains__('-dank'):
            # split the file name so we can get the extension
            splitname = fname.split('.')
            song = AudioSegment.from_file(fname, splitname[-1])
            # done with this unmodified file, erase it to save space on the server
            os.remove(fname)
            # grab just the juicy bass
            bass = song.low_pass_filter(50)
            # crank it up 316.22! (50dB)
            bass = bass + 50
            # layer in the original song so it keeps some resemblance
            bass_boost = song.overlay(bass)
            # normalize the audio to have 10db of headroom so we dont actually fuck up peoples ears
            bass_boost = bass_boost.normalize(10)
            fname = bass_boost.export(fname, format="mp3").name
        await Audio.playTrack(fname, ctx)
        # erase file to save server space
        os.remove(fname)
        return

    # plays the song with the given filename. filename must be relevant to the
    # directory the bot is in. ctx is the discord message context.
    async def playTrack(fileName, ctx):
        channel = ctx.author.voice.channel
        if not channel:
            return
        await channel.connect()
        source = FFmpegPCMAudio(fileName)
        ctx.voice_client.play(source)
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        await ctx.voice_client.disconnect()
        return
