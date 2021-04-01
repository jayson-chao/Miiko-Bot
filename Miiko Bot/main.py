# main.py
# main executable for bot

import os
import re
import random
from dotenv import load_dotenv
from discord.ext import commands

from emoji import miiko_emoji
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

    guild = await models.Guild.get_or_none(id=message.guild.id)
    if guild and guild.response_pref:
        if message.content == 'shut up, miiko': # a little easter egg command
            await models.Guild.update_or_create(id=message.guild.id, defaults={'response_pref':False})
            await message.channel.send('Set message response preference, nano!')
            return
        # some reactions to responses
        elif (re.search('ssh|ssh|quiet|shut up', message.content.lower())) and message.content[0] != CMD_PREFIX: 
            await message.channel.send(str(bot.get_emoji(822256196575559720)))
        elif re.search('nano', message.content.lower()) and message.content[0] != CMD_PREFIX: 
            if guild.react_pref:
                await message.add_reaction('🇳')
                await message.add_reaction('🇦')
                await message.add_reaction(str(bot.get(826923642264092682)))
                await message.add_reaction('🇴')
                await message.add_reaction('‼️')
            else:
                await message.channel.send('nano!')
    # emote reacts to character names, always on
    if re.search('miiko', message.content.lower()) and message.content[0] != CMD_PREFIX: 
        eid = random.choice(list(miiko_emoji.values()))
        await message.add_reaction(str(bot.get_emoji(eid)))
    elif re.search('haruna', message.content.lower()) and message.content[0] != CMD_PREFIX: 
        await message.add_reaction(str(bot.get_emoji(768398466753757214)))
        await message.add_reaction(str(bot.get_emoji(768398467005153322)))

    await bot.process_commands(message) # process commands, need bc on_message override

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)