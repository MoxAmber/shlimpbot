from typing import Optional

from nextcord import TextChannel
from nextcord.ext import commands
from nextcord.ext.commands import ExtensionError


class Utilities(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx: commands.Context, channel: Optional[TextChannel], *, text):
        if channel:
            await channel.send(text)
            return

        await ctx.send(text)

    @commands.group()
    async def extensions(self, ctx: commands.Context):
        pass

    @extensions.command(name='list')
    @commands.is_owner()
    async def list_extensions(self, ctx: commands.Context):
        await ctx.send(f'Currently loaded extensions: {" ".join([x for x in self.bot.extensions])}')

    @extensions.command(name='reload')
    @commands.is_owner()
    async def reload_extension(self, ctx: commands.Context, *, name):
        try:
            self.bot.reload_extension(name)
        except ExtensionError as error:
            await ctx.send(str(error))
        else:
            await ctx.send('Extension reloaded')

    @extensions.command(name='load')
    @commands.is_owner()
    async def load_extension(self, ctx: commands.Context, *, name):
        try:
            self.bot.load_extension(name)
        except ExtensionError as error:
            await ctx.send(error.message)
        else:
            await ctx.send('Extension loaded')

    @extensions.command(name='unload')
    @commands.is_owner()
    async def unload_extension(self, ctx: commands.Context, *, name):
        try:
            self.bot.unload_extension(name)
        except ExtensionError as error:
            await ctx.send(error.message)
        else:
            await ctx.send('Extension unloaded')

    @extensions.command(name='reload_all')
    @commands.is_owner()
    async def reload_all_extensions(self, ctx: commands.Context):
        for extension in self.bot.extensions:
            try:
                self.bot.reload_extension(extension)
            except ExtensionError as error:
                await ctx.send(str(error))
                break
        else:
            await ctx.send('All extensions reloaded successfully')


def setup(bot: commands.Bot):
    bot.add_cog(Utilities(bot))
