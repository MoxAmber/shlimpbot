import json
import random
from typing import Optional

import pkg_resources
from nextcord import TextChannel
from nextcord.ext import commands

from shlimpbot.bot import config
from shlimpbot.checks import is_config_channel


class Wordle(commands.Cog):
    """Wordle"""

    def __init__(self, bot):
        self.bot = bot
        self.current_word: Optional[str] = None
        self.guesses = 0

    @commands.group()
    async def wordle(self, ctx):
        pass

    @wordle.command(name='start')
    @commands.guild_only()
    @is_config_channel('wordle.channel')
    async def start(self, ctx):
        if not self.current_word:
            with pkg_resources.resource_stream(__name__, 'data/answers.json') as answer_file:
                answers = json.load(answer_file)
            self.current_word = random.choice(answers['5'])
            await ctx.send('⬛⬛⬛⬛⬛')
        else:
            await ctx.send('Game already running!')

    @wordle.command('guess')
    @commands.guild_only()
    @is_config_channel('wordle.channel')
    async def guess(self, ctx, *, arg: str):
        with pkg_resources.resource_stream(__name__, 'data/words.json') as guess_file:
            valid_guesses = json.load(guess_file)
        if arg not in valid_guesses['5']:
            await ctx.reply('Invalid guess')
            return

        self.guesses += 1
        response = ''
        for idx, letter in enumerate(arg):
            if letter == self.current_word[idx]:
                response += '🟩'
            elif letter in self.current_word:
                response += '🟨'
            else:
                response += '⬛'

        if self.guesses == 6 and not arg == self.current_word:
            response += f'\nGame over, the word was {self.current_word}'

        if arg == self.current_word:
            response += '\nCongratulations!'

        await ctx.reply(response)

        if self.guesses == 6 or arg == self.current_word:
            self.current_word = None
            self.guesses = 0

    @wordle.command('channel')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def set_channel(self, ctx, *, channel: TextChannel):
        config.set_server(ctx.guild.id, 'wordle.channel', channel.id)
        await ctx.send(f'Wordle channel set to {channel.mention}')


def setup(bot):
    bot.add_cog(Wordle(bot))
