# utility.py
# Utility Commands for Miiko Bot

import discord
from discord.ext import commands
from bot import MiikoBot

class Utility(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='test command & response')
    async def ping(self, ctx):
        await ctx.send('pong, nano!')

    @commands.command(name='admin', help='test admin-only command')
    @commands.has_permissions(administrator=True)
    async def admin_ping(self, ctx):
        response = 'admin, nano!'
        await ctx.send(response)

    @commands.command(name='info', help='information on MiikoBot')
    async def info_embed(self, ctx):
        infoEmbed=discord.Embed(title="MiikoBot", description="A D4DJ utility bot. Currently in development!")
        await ctx.send(embed=infoEmbed)

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))