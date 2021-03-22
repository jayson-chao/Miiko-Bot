# music.py
# music commands for bot

import discord
from discord.ext import commands
from bot import MiikoBot

FFMPEG_PATH="C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe" # change to users' ffmpeg path

class VoiceError(Exception):
    pass

class Music (commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='has Miiko join user\'s voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            raise VoiceError('You are not connected to a voice channel')

        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send('Connected, nano!')

    @commands.command(name='leave', help='has Miiko leave voice channel')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('leave: Bot is not connected to any voice channel')

        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected, nano!')

    # currently plays though to end, does not allow more play commands
    @commands.command(name='play', help='has Miiko play her favorite song!')
    async def play(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('play: Bot is not connected to any voice channel')
        audio = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source='nyan.mp3')
        ctx.voice_client.play(audio)

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Music(bot))