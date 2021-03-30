# main.py
# main executable for bot

import os
import re
from dotenv import load_dotenv
from discord.ext import commands

from bot import MiikoBot
import models

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Hidden
CMD_PREFIX = '&'

bot = MiikoBot(command_prefix=CMD_PREFIX)

# load extra extensions for bot
bot.load_extension('commands.utility')
bot.load_extension('commands.music')
bot.load_extension('commands.preference')

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')
    print(f'Server count: {len(bot.guilds)}')
    for guild in bot.guilds:
        await models.Guild.update_or_create(id=guild.id, defaults={'name': guild.name})

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

    # if not bot command and contains 'nano', echo 'nano'
    guild = await models.Guild.get_or_none(id=message.guild.id)
    if guild and guild.basic_pref:
        if re.search('nano', message.content.lower()) and message.content[0] != CMD_PREFIX: 
            await message.channel.send('nano!')

    await bot.process_commands(message) # process commands, need bc on_message override

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)