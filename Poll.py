import discord
import asyncio
from ColdOneCore import CoreColors


class Poll:

    # This feels unspeakably wrong
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    # Creates a poll and sends its embed
    @staticmethod
    async def createPoll(ctx, bot):
        author = ctx.author.name
        pollOptions = ctx.message.content.split(',')
        embed = discord.Embed(author=author, title='poll',
                              color=CoreColors.InteractColor)
        pollText = ''
        index = 0
        numberOfOptions = 0
        # make sure we have at least one poll option
        if len(pollOptions) > 0:
            poll_question = pollOptions[0]
            # ignore the first 6 characters since they are the bot command
            poll_question = poll_question[6:]
            pollText += poll_question + '\r\n'
            # yeet the poll text, it's not needed anymore
            pollOptions.pop(0)
        else:
            return
        for option in pollOptions:
            pollText += Poll.numbers[index]+' '+option+'\r\n'
            index += 1
            numberOfOptions += 1
        pollText += 'This poll will close after 15 minutes. End it early with 🛑'
        embed.description = pollText
        sentEmbedMsg = await ctx.channel.send(embed=embed)
        index = 0
        for i in range(numberOfOptions):
            await sentEmbedMsg.add_reaction(Poll.numbers[index])
            index += 1
        PollTimer(Poll.closePoll, sentEmbedMsg, pollOptions, bot)

    @staticmethod
    async def closePoll(message, opts):
        print('closing poll')
        options = [0] * len(opts)
        index = 0
        # tally up the scores for each option
        for curReact in message.reactions:
            print(curReact)
            if curReact.emoji in Poll.numbers:

                # lookup the index of this option in the numbers list
                masterIdx = Poll.numbers.index(curReact.emoji)
                print('idx: '+str(masterIdx))
                # if the emoji is actually used in this poll
                if masterIdx <= len(opts):
                    print(curReact.emoji + ' '+str(curReact.count))
                    options[masterIdx] = curReact.count
        winnerIdx = 0
        winnerVotes = 1  # all options have one react from the bot
        index = 0
        # figure out who got the most votes
        for count in options:
            if count > winnerVotes:
                winnerVotes = count
                winnerIdx = index
            index += 1
        await message.channel.send('winner: '+Poll.numbers[winnerIdx]+' with '
                                   + str(winnerVotes - 1) + ' votes!')


class PollTimer:
    def __init__(self, callback, message, opts, bot):
        self._callback = callback
        self._message = message
        self._opts = opts
        self._task = asyncio.ensure_future(self._job())
        self._running = True
        self._bot = bot

    async def _job(self):
        while self._running:
            sleepTime = 900  # 15 minutes
            updateInterval = 15
            for i in range(0, sleepTime, updateInterval):
                await asyncio.sleep(updateInterval)
                channel = await self._bot.fetch_channel(self._message.channel.id)
                cur_message = await channel.fetch_message(self._message.id)
                for reacts in cur_message.reactions:
                    if '🛑' == reacts.emoji:
                        await self._callback(cur_message, self._opts)
                        self._task.cancel()
                        return
            await self._callback(self._message, self._opts)
            self._task.cancel()

    def is_alive(self):
        return self._running

    def cancel(self):
        self._running = False
        self._task.cancel()
