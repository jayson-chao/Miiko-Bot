# main.py
# main executable for bot

import os
import re
from bot import MiikoBot
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Hidden
CMD_PREFIX = '&'

bot = MiikoBot(command_prefix=CMD_PREFIX)

# load extra extensions for bot
bot.load_extension('commands.utility')
bot.load_extension('commands.music')

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # if not bot command and contains 'nano', echo 'nano'
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