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

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Preference(bot))