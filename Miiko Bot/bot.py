# bot.py
# first test file for running discord bot

import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} is connected to Discord.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    response = "nano!"
    await message.channel.send(response)

client.run(TOKEN)