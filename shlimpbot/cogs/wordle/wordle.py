import json
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Dict, Union

import pkg_resources
from nextcord import TextChannel, Thread
from nextcord.ext import commands

from shlimpbot.cogs.config import is_config_channel


@dataclass
class ChannelState:
    word: Optional[str] = None
    guesses: int = 0


class Wordle(commands.Cog):
    """Wordle"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.state: Dict[int, ChannelState] = defaultdict(ChannelState)

    @commands.group()
    async def wordle(self, ctx: commands.Context):
        pass

    @wordle.command(name='cheat')
    @is_config_channel('wordle.channel')
    async def get_word(self, ctx: commands.Context):
        current_state = self.state[ctx.channel.id]
        await ctx.send(current_state.word or "No game in progress")

    @wordle.command(name='start')
    @is_config_channel('wordle.channel')
    async def start(self, ctx: commands.Context, *, length: int = 5):
        current_state = self.state[ctx.channel.id]
        if current_state.word:
            await ctx.send('Game already running!')
            return

        with pkg_resources.resource_stream(__name__, 'data/answers.json') as answer_file:
            answers = json.load(answer_file)

        if length > 7 or length < 4:
            await ctx.send('Sorry I only know words between 4 and 7 letters long')
            return
        current_state.word = random.choice(answers[str(length)])
        await ctx.send('⬛' * len(current_state.word))

    @wordle.command('guess')
    @is_config_channel('wordle.channel')
    async def guess(self, ctx: commands.Context, *, guess: str):
        current_state = self.state[ctx.channel.id]
        if not current_state.word:
            await ctx.send('Game not running. Use command `wordle start` to begin')
            return

        with pkg_resources.resource_stream(__name__, 'data/words.json') as guess_file:
            valid_guesses = json.load(guess_file)

        if guess not in valid_guesses[str(len(current_state.word))]:
            await ctx.reply('Invalid guess')
            return

        current_state.guesses += 1
        response = ['⬛'] * len(current_state.word)

        letter_counts = {letter: current_state.word.count(letter) for letter in current_state.word}

        for idx, letter in enumerate(guess):
            if current_state.word[idx] == letter:
                response[idx] = '🟩'
                letter_counts[letter] -= 1

        for idx, letter in enumerate(guess):
            if current_state.word[idx] != letter and letter_counts.get(letter, 0) > 0:
                response[idx] = '🟨'
                letter_counts[letter] -= 1

        response = ''.join(response)

        if current_state.guesses == 6 and not guess == current_state.word:
            response += f"\nGame over, the word was {current_state.word}"

        if guess == current_state.word:
            response += '\nCongratulations!'

        await ctx.reply(response)

        if current_state.guesses == 6 or guess == current_state.word:
            self.state.pop(ctx.channel.id)

    @wordle.command('channel')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def set_channel(self, ctx: commands.Context, *, channel: Union[TextChannel, Thread]):
        config = self.bot.get_cog('Config')
        await config.set_guild(ctx, 'wordle.channel', data=channel.id)
        await ctx.send(f'Wordle channel set to {channel.mention}')


def setup(bot):
    bot.add_cog(Wordle(bot))
