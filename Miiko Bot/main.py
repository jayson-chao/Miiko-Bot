# main.py
# main executable for bot

import json
import re
import random
import redis
import sys
import discord
from discord.ext import commands

from common.emoji import miiko_emoji
from bot import MiikoBot
import models

redis_server = redis.Redis() # Create access to Redis
TOKEN = str(redis_server.get('AUTH_TOKEN').decode('utf-8'))
CMD_PREFIX = '&'

bot = MiikoBot(command_prefix=CMD_PREFIX)

# load extra extensions for bot
EXTS = ['event', 'utility', 'music', 'player', 'preference']
for e in EXTS:
    bot.load_extension(f'commands.{e}')

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')
    print(f'Server count: {len(bot.guilds)}')
    for guild in bot.guilds:
        await models.Guild.update_or_create(id=guild.id, defaults={'name': guild.name})
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
