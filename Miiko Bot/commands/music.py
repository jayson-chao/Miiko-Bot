# music.py
# music commands for bot

import discord
from discord.ext import commands
from discord import ClientException
from bot import MiikoBot

FFMPEG_PATH="C:/Program Files/FFmpeg/bin/ffmpeg.exe" # change to users' ffmpeg path

class VoiceError(Exception):
    pass

# 2021-03-23 issue encountered (unreplicated after 4 attempts)
# Encountered issue where having Miiko join two VCs in two different servers led to the Miiko
# instance in the second server to malfunction on join/leave commands (thought she wasn't in
# a VC) and ignore play commands completely. Might've been an issue of two Miiko main.py commands
# running in parallel?

class Music (commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='has Miiko join and lurk in user\'s voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            raise VoiceError('You are not connected to a voice channel')

        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
            await ctx.send('Connected, nano!')
            return
        await ctx.voice_client.move_to(channel)
        await ctx.send('Moved channels, nano!')
        

    @commands.command(name='leave', aliases=['disconnect', 'dc'], help='has Miiko leave voice channel')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('leave: Bot is not connected to any voice channel')

        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected, nano!')

    # currently plays though to end, does not allow more play commands
    @commands.command(name='play', hidden=True, help='has Miiko play her favorite song!')
    async def play(self, ctx, id):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('play: Bot is not connected to any voice channel')
        try:
            audio = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=f'common/assets/music/{id}.mp3')
        except:
            await ctx.send('Invalid song ID, nano!')
            raise VoiceError('play: Invalid song ID was passed')
        try:
            ctx.voice_client.play(audio)
        except ClientException as err:
            errstr = str(err)
            await ctx.send(f'Error: {err}')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Music(bot))