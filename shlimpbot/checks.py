from nextcord.ext import commands

from shlimpbot.bot import config


def is_config_channel(config_key: str):
    async def check_channel(ctx: commands.Context):
        config_channel = config.get_server(ctx.guild.id, config_key)
        return ctx.channel.id == config_channel

    return commands.check(check_channel)
