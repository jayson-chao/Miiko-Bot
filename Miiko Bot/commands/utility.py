# utility.py
# Utility Commands for Miiko Bot

import discord
from discord.ext import commands
from tortoise import Tortoise

from bot import MiikoBot
import load_db
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
        await self.bot.close() # Throwing runtime err on windows (but not ubuntu) - apparently this is a known bug in the discord.py library

    @commands.command(name='reload', help='reloads all extensions', hidden=True)
    @commands.is_owner()
    async def reload_bot(self, ctx):
        self.bot.reload_all_extensions()
        await ctx.send('Bot has been reloaded!')

    @commands.command(name='refresh', help='refresh db', hidden=True)
    @commands.is_owner()
    async def refresh_db(self, ctx):
        await load_db.load_db()
        await ctx.send('DB Refreshed!')
        

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))