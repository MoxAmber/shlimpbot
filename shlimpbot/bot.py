import logging
import os

from nextcord.ext import commands

from .config import Config

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="~")
config = Config(os.getenv('SHLIMPBOT_SETTINGS', './settings.json'))


def run():
    bot.load_extension('shlimpbot.utilities')
    bot.run(config.get_global('discord.token'))


if __name__ == "__main__":
    run()
