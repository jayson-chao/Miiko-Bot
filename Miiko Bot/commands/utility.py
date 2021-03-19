# utility.py
# Utility Commands for Miiko Bot

from discord.ext import commands
from bot import MiikoBot

class Utility(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='test command & response')
    async def shh_nano(ctx):
        response = 'pong, nano!'
        await ctx.send(response)

    @commands.command(name='admin', help='test admin-only command')
    @commands.has_permissions(administrator=True)
    async def admin_ping(ctx):
        response = 'admin, nano!'
        await ctx.send(response)

# required for adding cog to bot, MiikoBot's load_extension expects it
def setup(bot):
    bot.add_cog(Utility(bot))