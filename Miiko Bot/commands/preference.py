# preference.py
# Preference Settings for Miiko Bot - set on a server-by-server basis.

import discord
from discord.ext import commands

from bot import MiikoBot
import models

bool_true_strings = {'True', 'true', 'on'}
bool_false_strings = {'False', 'false', 'off'}
bool_strings = bool_true_strings | bool_false_strings

def is_bool_string(s: str):
    return s in bool_strings

# assumes that this is invoked after string is validated by is_bool_string
def string_to_bool(s: str):
    return s in bool_true_strings

class Preference(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setpref', help='set value of test pref setting (whether miiko responds to \'nano\')')
    @commands.has_permissions(administrator=True)
    async def set_pref(self, ctx, value):
        if is_bool_string(value):
            await models.Guild.update_or_create(id=ctx.guild.id, defaults={'basic_pref':string_to_bool(value)})
            await ctx.send('Set preference, nano!')
        else:
            await ctx.send('Invalid preference setting, nano!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Preference(bot))