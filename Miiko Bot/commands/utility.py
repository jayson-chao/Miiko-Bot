# utility.py
# Utility Commands for Miiko Bot

import json
import os
import discord
from discord.ext import commands

from bot import MiikoBot
from load_db import load_db
import models

class Utility(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='test command & response', hidden=True)
    async def ping(self, ctx):
        await ctx.send('Pong, nano!')

    @commands.command(name='info', help='information on MiikoBot')
    async def info_embed(self, ctx):
        infoEmbed = discord.Embed(title="MiikoBot", description="A D4DJ utility bot. Currently in early development!")
        await ctx.send(embed=infoEmbed)

    @commands.command(name='archive', help='links to the general d4dj archive')
    async def archive_embed(self, ctx):
        archiveEmbed = discord.Embed(title="D4DJ Archive", description="[Click Here!](https://tinyurl.com/d4djarchive)")
        await ctx.send(embed=archiveEmbed)

    @commands.command(name='shutdown', help='shuts down MiikoBot', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send('Shutting down, nano!')
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.logout() # will throw Runtime Error - apparently this is a known bug on their end

    @commands.command(name='refresh', help='reloads all data', hidden=True)
    async def refresh_db(self, ctx):
        await load_db()
        await ctx.send('Reloaded data!')

    @commands.command(name='reload', help='reloads all extensions', hidden=True)
    async def reload_bot(self, ctx):
        self.bot.reload_all_extensions()
        await ctx.send('Bot has been reloaded!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))