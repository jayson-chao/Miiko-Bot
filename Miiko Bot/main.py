# main.py
# main executable for bot

import json
import os
import re
import random
import sys
import discord
from dotenv import load_dotenv
from discord.ext import commands

from masters import dbs, exts
from common.emoji import miiko_emoji
from bot import MiikoBot
import models

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Hidden
CMD_PREFIX = '&'

bot = MiikoBot(command_prefix=CMD_PREFIX)

def str_to_cls(str):
    try:
        return getattr(sys.modules[__name__], str)
    except AttributeError:
        raise NameError(f'CLASS({str}) does not exist')

# load db func to load/reload json data (might need to clear db here as extra preventative measure)
async def load_db():
    for m in dbs:
        mtype = getattr(models, f'D4DJ{m}')
        await mtype.all().delete()
        with open(f'Master/{m}Master.json') as f:
            data = json.load(f)
        for item in data:
            await mtype.update_or_create(id=item, defaults=data[item])

# load extra extensions for bot
for e in exts:
    bot.load_extension(f'commands.{e}')

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')
    print(f'Server count: {len(bot.guilds)}')
    for guild in bot.guilds:
        await models.Guild.update_or_create(id=guild.id, defaults={'name': guild.name})
    await load_db()
    await bot.change_presence(activity=discord.Game(status=discord.Status.online, name="&help for help, nano!"))

@bot.listen()
async def on_guild_join(guild):
    await models.Guild.update_or_create(id=guild.id, defaults={'name': guild.name})

@bot.listen()
async def on_guild_remove(guild):
    await (await models.Guild.get(id=guild.id)).delete()

@bot.listen()
async def on_guild_update(before, after):
    await models.Guild.update_or_create(id=after.id, defaults={'name': after.name})

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # process non-command-prefixed messages

    await bot.process_commands(message) # process commands, need bc on_message override

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)