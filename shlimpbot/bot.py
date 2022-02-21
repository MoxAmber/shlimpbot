import json
import logging
import os

from nextcord.ext import commands

logging.basicConfig(level=logging.INFO)

with open(os.getenv('SHLIMPBOT_SETTINGS', './settings.json')) as config_file:
    config = json.load(config_file)['global']

bot = commands.Bot(command_prefix='!')


@bot.listen('on_command_error')
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❌')


def run():
    for extension in config['extensions']:
        bot.load_extension(extension)
    bot.run(config['discord']['token'])


if __name__ == "__main__":
    run()
