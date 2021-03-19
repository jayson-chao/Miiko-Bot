# bot.py
# first test file for running discord bot

import os
import re
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Hidden
CMD_PREFIX = '&'

bot = commands.Bot(command_prefix=CMD_PREFIX)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to Discord.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if re.search('nano', message.content.lower()) and message.content[0] != CMD_PREFIX: 
        await message.channel.send('nano!')

    await bot.process_commands(message) # process commands, need bc on_message override

@bot.command(name='ping', help='test command & response')
async def shh_nano(ctx):
    response = 'pong, nano!'
    await ctx.send(response)

@bot.command(name='admin', help='test admin-only command')
@commands.has_permissions(administrator=True)
async def admin_ping(ctx):
    response = 'admin, nano!'
    await ctx.send(response)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)