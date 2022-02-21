import json
import logging
import os
from typing import cast

from jsonpath_ng import parse
from nextcord.ext import commands, tasks


def is_config_channel(config_key: str):
    async def check_channel(ctx: commands.Context):
        if not ctx.guild:
            # We're in a DM of some sort, so it's always allowed.
            return True
        config = cast(Config, ctx.bot.get_cog('Config'))
        config_channel = await config.get_guild(ctx, config_key)
        return ctx.channel.id == config_channel

    return commands.check(check_channel)


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('shlimpbot.cogs.config')
        self._config = {}
        self._filename = os.getenv('SHLIMPBOT_SETTINGS', './settings.json')

        with open(self._filename) as config_file:
            self._config = json.load(config_file)

        self.writer.start()
        self.logger.info('Loaded shlimpbot.cogs.config')

    def cog_unload(self):
        self.logger.info('Unloading shlimpbot.cogs.config')
        self.writer.stop()
        self.write_config()

    @tasks.loop(minutes=5)
    async def writer(self):
        self.logger.info('Writing settings')
        with open(self._filename, 'w') as config_file:
            json.dump(self._config, config_file)

    @commands.group()
    @commands.is_owner()
    async def config(self, ctx: commands.Context):
        pass

    @config.command('write')
    @commands.is_owner()
    async def write_config(self, ctx: commands.Context):
        with open(self._filename, 'w') as config_file:
            json.dump(self._config, config_file)

    @config.group()
    async def get(self, ctx: commands.Context):
        pass

    @config.group()
    async def set(self, ctx: commands.Context):
        pass

    @get.command(name='global')
    @commands.is_owner()
    async def get_global(self, ctx: commands.Context, *, path: str):
        jsonpath_expr = parse(f'$.global.{path}')
        if matches := jsonpath_expr.find(self._config):
            if 'config' in ctx.invoked_parents:
                await ctx.send(str(matches[0].value))
            return matches[0].value

    @get.command(name='guild')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def get_guild(self, ctx: commands.Context, *, path: str):
        jsonpath_expr = parse(f'$.guilds."{ctx.guild.id}".{path}')
        if matches := jsonpath_expr.find(self._config):
            if 'config' in ctx.invoked_parents:
                await ctx.send(str(matches[0].value))
            return matches[0].value

    @get.command(name='user')
    @commands.dm_only()
    async def get_user(self, ctx: commands.Context, *, path: str):
        jsonpath_expr = parse(f'$.users."{ctx.author.id}".{path}')
        if matches := jsonpath_expr.find(self._config):
            if 'config' in ctx.invoked_parents:
                await ctx.send(str(matches[0].value))
            return matches[0].value

    @set.command(name='global')
    @commands.is_owner()
    async def set_global(self, ctx, path: str, *, data: str):
        jsonpath_expr = parse(f'$.global.{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_global(ctx, path=path)

    @set.command(name='guild')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def set_guild(self, ctx, path: str, *, data: str):
        jsonpath_expr = parse(f'$.guilds."{ctx.guild.id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_guild(ctx, path=path)

    @set.command(name='user')
    @commands.dm_only()
    async def set_user(self, ctx, path: str, *, data: str):
        jsonpath_expr = parse(f'$.users."{ctx.author.id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_user(ctx, path=path)


def setup(bot: commands.Bot):
    bot.add_cog(Config(bot))
