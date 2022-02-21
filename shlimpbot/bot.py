import logging
import os

from nextcord.ext import commands

from .config import Config

logging.basicConfig(level=logging.INFO)

config = Config(os.getenv('SHLIMPBOT_SETTINGS', './settings.json'))
bot = commands.Bot(command_prefix=config.get_global('prefix'))


@bot.listen('on_command_error')
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❌')


def run():
    for extension in config.get_global('extensions'):
        bot.load_extension(extension)
    bot.run(config.get_global('discord.token'))


if __name__ == "__main__":
    run()
