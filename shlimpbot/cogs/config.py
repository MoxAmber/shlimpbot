import json
import logging
import os
from typing import Optional

from jsonpath_ng import parse
from nextcord import Message
from nextcord.ext import commands, tasks
from nextcord.ext.commands.view import StringView


def is_config_channel(config_key: str):
    async def check_channel(ctx: commands.Context):
        if not ctx.guild:
            # We're in a DM of some sort, so it's always allowed.
            return True
        config = ctx.bot.get_cog('Config')
        config_channel = await config.get_guild(ctx, path=config_key)
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

        self.bot.command_prefix = get_prefix
        self.writer.start()
        self.logger.info('Loaded shlimpbot.cogs.config')

    def cog_unload(self):
        self.logger.info('Unloading shlimpbot.cogs.config')
        self.writer.stop()
        self.write_config()

    def write_config(self):
        with open(self._filename, 'w') as config_file:
            json.dump(self._config, config_file)

    @tasks.loop(minutes=5)
    async def writer(self):
        self.logger.info('Writing settings')
        self.write_config()

    # General utility config commands

    @commands.group()
    @commands.is_owner()
    async def config(self, ctx: commands.Context):
        pass

    @config.command('write')
    @commands.is_owner()
    async def write_config_cmd(self, ctx: commands.Context):
        self.write_config()

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
    async def set_global(self, ctx, path: str, *, data):
        jsonpath_expr = parse(f'$.global.{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_global(ctx, path=path)

    @set.command(name='guild')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def set_guild(self, ctx, path: str, *, data):
        jsonpath_expr = parse(f'$.guilds."{ctx.guild.id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_guild(ctx, path=path)

    @set.command(name='user')
    @commands.dm_only()
    async def set_user(self, ctx, path: str, *, data):
        jsonpath_expr = parse(f'$.users."{ctx.author.id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        return await self.get_user(ctx, path=path)

    # more specific commands
    @commands.group()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def prefixes(self, ctx: commands.Context):
        pass

    @prefixes.command(name='set')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def set_prefixes(self, ctx: commands.Context, *prefixes) -> Optional[list[str]]:
        new_value = await self.set_guild(ctx, 'prefixes', data=list(prefixes))
        await ctx.send(f'Guild prefixes set to: {", ".join(new_value)}')
        return new_value

    @prefixes.command(name='get')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def get_prefixes(self, ctx: commands.Context) -> Optional[list[str]]:
        value = await self.get_guild(ctx, path='prefixes')
        if ctx.command == self.get_prefixes:
            if not value:
                default_prefix = await self.get_global(ctx, path='prefix') or '!'
                await ctx.send(
                    f"No prefixes currently set, using the bot default: {default_prefix}")
            await ctx.send(f'Current guild prefixes: {", ".join(value)}')
        return value

    @prefixes.command(name='add')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def add_prefix(self, ctx: commands.Context, prefix: str):
        prefixes = await self.get_prefixes(ctx)
        if not prefixes:
            await self.set_prefixes(ctx, prefix)

        prefixes.extend(prefix)
        prefixes = set(prefixes)
        await self.set_prefixes(ctx, *prefixes)

    @prefixes.command(name='remove')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def remove_prefix(self, ctx: commands.Context, prefix: str):
        prefixes = await self.get_prefixes(ctx)

        if not prefixes or prefix not in prefixes:
            await ctx.send(f'{prefix} is not currently set as a prefix')

        prefixes.remove(prefix)
        await self.set_prefixes(ctx, *prefixes)


def setup(bot: commands.Bot):
    bot.add_cog(Config(bot))


async def get_prefix(bot: commands.Bot, message: Message):
    bot_config = bot.get_cog('Config')
    if not bot_config:
        return '!'

    ctx = commands.Context(prefix=None, message=message, bot=bot, view=StringView(message.content))
    prefixes = ['!']
    if not message.guild:
        prefixes = await bot_config.get_global(ctx, path='prefixes')
    else:
        guild_prefixes = await bot_config.get_guild(ctx, path='prefixes')
        if guild_prefixes:
            prefixes = guild_prefixes

    return commands.when_mentioned_or(*prefixes)(bot, message)
