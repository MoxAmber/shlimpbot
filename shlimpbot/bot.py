import logging
import os

import yaml
from nextcord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('shlimpbot.bot')

with open(os.getenv('SHLIMPBOT_SETTINGS', './settings.yaml')) as config_file:
    config = yaml.safe_load(config_file)['global']

bot = commands.Bot(command_prefix='!')


@bot.listen('on_command_error')
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❌')
    else:
        logger.exception(error)


def run():
    for extension in config['extensions']:
        bot.load_extension(extension)
    bot.run(config['discord']['token'])


if __name__ == "__main__":
    run()
