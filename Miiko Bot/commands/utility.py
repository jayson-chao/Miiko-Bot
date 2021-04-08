# utility.py
# Utility Commands for Miiko Bot

import os
import discord
from discord.ext import commands

from bot import MiikoBot
import models

class Utility(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='test command & response', hidden=True)
    async def ping(self, ctx):
        await ctx.send('pong, nano!')

    @commands.command(name='admin', help='test admin-only command', hidden=True)
    @commands.has_permissions(administrator=True)
    async def admin_ping(self, ctx):
        response = 'admin, nano!'
        await ctx.send(response)

    @commands.command(name='info', help='information on MiikoBot')
    async def info_embed(self, ctx):
        infoEmbed = discord.Embed(title="MiikoBot", description="A D4DJ utility bot. Currently in development!")
        await ctx.send(embed=infoEmbed)

    @commands.command(name='shutdown', help='shuts down MiikoBot', hidden=True)
    async def shutdown(self, ctx):
        TOKEN = os.getenv('BOT_OWNER')
        if ctx.author.id == int(TOKEN):
            await ctx.send('Shutting down, nano!')
            await self.bot.logout() # will throw Runtime Error - apparently this is a known bug on their end
        await ctx.send('I don\'t take orders from you, nano!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))