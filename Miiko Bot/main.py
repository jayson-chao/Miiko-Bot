# main.py
# main executable for bot

import json
import os
import re
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

from emoji import miiko_emoji
from bot import MiikoBot
import models

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Hidden
CMD_PREFIX = '&'

bot = MiikoBot(command_prefix=CMD_PREFIX)

# load db func to load/reload json data (might need to clear db? unsure if to do that here or on shutdown)
async def load_db():
    with open('Master/EventMaster.json') as f:
        data = json.load(f)

    for live in data:
        await models.D4DJEvent.update_or_create(id=live, defaults=data[live])

# load extra extensions for bot
bot.load_extension('commands.utility')
bot.load_extension('commands.music')
bot.load_extension('commands.preference')
bot.load_extension('commands.event')

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')
    print(f'Server count: {len(bot.guilds)}')
    for guild in bot.guilds:
        await models.Guild.update_or_create(id=guild.id, defaults={'name': guild.name})
    await load_db()
    await bot.change_presence(activity=discord.Game(name="Surprise, nano!"))

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