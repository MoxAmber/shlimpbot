import logging
import os

from nextcord.ext import commands

from .config import Config

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="~")
config = Config(os.getenv('SHLIMPBOT_SETTINGS', './settings.json'))


def run():
    for extension in config.get_global('extensions'):
        bot.load_extension(extension)
    bot.run(config.get_global('discord.token'))


if __name__ == "__main__":
    run()
