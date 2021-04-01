# utility.py
# Utility Commands for Miiko Bot

import discord
from discord.ext import commands

from bot import MiikoBot
import models

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

    @commands.command(name='setchannel', help='set channel to send bot messages to')
    @commands.has_permissions(manage_guild=True)
    async def set_channel(self, ctx, channel_id):
        if channel_id.isdigit():
            await models.Guild.update_or_create(id=ctx.guild.id, defaults={'msg_channel':int(channel_id)})
            await ctx.send('Set message channel preference, nano!')
        else:
            await ctx.send('Invalid channel setting, nano!')

    @commands.command(name='send', help='send message as bot in set channel')
    @commands.has_permissions(manage_guild=True)
    async def send_message(self, ctx, message):
        guild = await models.Guild.get_or_none(id=ctx.guild.id)
        if guild:
            channel = self.bot.get_channel(guild.msg_channel)
            # make sure bot is sending to a channel within the server - don't want cross-server posting
            if channel and channel in ctx.guild.channels: 
                await channel.send(message)
            else:
                await ctx.send('Invalid channel set, nano!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Utility(bot))