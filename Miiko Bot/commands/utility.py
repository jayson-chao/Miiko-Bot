# utility.py
# Utility Commands for Miiko Bot

import json
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
        infoEmbed = discord.Embed(title="MiikoBot", description="A D4DJ utility bot. Currently in early development!")
        await ctx.send(embed=infoEmbed)

    @commands.command(name='archive', help='links to the general d4dj archive')
    async def archive_embed(self, ctx):
        archiveEmbed = discord.Embed(title="D4DJ Archive", description="[Click Here!](https://tinyurl.com/d4djarchive)")
        await ctx.send(embed=archiveEmbed)

    @commands.command(name='shutdown', help='shuts down MiikoBot', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down, nano!')
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.logout() # will throw Runtime Error - apparently this is a known bug on their end

    # this is specific to reloading the event db for now but will need to make more general for all master
    @commands.command(name='refresh', help='reloads all data', hidden=True)
    async def refresh_db(self, ctx):
        await models.D4DJEvent.all().delete()
        with open('Master/EventMaster.json') as f: # loop into a 'for []master' file, then load into 'd4dj[]' model. eval() for models?
            data = json.load(f)
        for live in data:
            await models.D4DJEvent.update_or_create(id=live, defaults=data[live])
        await ctx.send('Reloaded data, nano!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))