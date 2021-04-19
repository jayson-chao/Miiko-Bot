# music.py
# music commands for bot

from queue import SimpleQueue
import asyncio
import discord
from discord.ext import commands
from discord import ClientException

import models
from bot import MiikoBot
from common.react_msg import run_paged_message
from common.aliases import unit_aliases, artists, process_artist

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
        if ctx.guild.id not in self.bot.player: # reset queue if there is none
            self.bot.player[ctx.guild.id] = SimpleQueue()
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
            await ctx.send("Connected, nano!")
            return
        if ctx.voice_client.channel is not channel:
            await ctx.voice_client.move_to(channel)
            await ctx.send("Moved, nano!")

    @commands.command(name='leave', aliases=['disconnect', 'dc'], help='has Miiko leave voice channel')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('leave: Bot is not connected to any voice channel')
        self.bot.player[ctx.guild.id] = SimpleQueue()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected, nano!')

    # currently plays though to end, does not allow more play commands
    @commands.command(name='play', hidden=True, help='play song')
    async def play(self, ctx, id=None):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('play: Bot is not connected to any voice channel')
        if ctx.voice_client.is_paused() and not id:
            ctx.voice_client.resume()
            return
        # need a none check against audio
        self.bot.player[ctx.guild.id].put((id, discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=f'common/assets/music/{id}.mp3')))
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await ctx.send(f'{id} placed in song queue')
        else:
            self.play_next(ctx)

    def play_next(self, ctx):
        if not ctx.voice_client: 
            return # disconnect handles stop()
        if self.bot.player[ctx.guild.id].empty():
            ctx.voice_client.stop() # need to stop for good - was running into glitch where if queue stopped then refilled, the first added song would trip an error
            asyncio.run_coroutine_threadsafe(ctx.send("Queue finished, nano!"), self.bot.loop)
            return
        next_song = self.bot.player[ctx.guild.id].get()
        asyncio.run_coroutine_threadsafe(ctx.send(f'Now playing {next_song[0]}'), self.bot.loop)
        self.bot.playing[ctx.guild.id] = next_song[0]
        ctx.voice_client.play(next_song[1], after=lambda e:self.play_next(ctx))

    @commands.command(name='skip', hidden=True, help='skip the current song')
    async def skip(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop() # don't need play_next, stop() will trigger vc.play.after

    @commands.command(name='pause', hidden=True, help='pause the song')
    async def pause(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(name='stop', hidden=True, help='stop playing song')
    async def stop(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel, nano!')
            raise VoiceError('stop: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing():
            self.bot.player[ctx.guild.id] = SimpleQueue() # empty queue before triggering vc.play.after
            ctx.voice_client.stop()

    @commands.command(name='np', aliases=['nowplaying'], hidden=True, help='display info for current song')
    async def now_playing(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.send(f'PLAYING: {self.bot.playing[ctx.guild.id]}')
        else:
            await ctx.send('Not playing anything, nano!')

    def song_name(self, s):
        if s.jpname: # change to guild preference later between en/jp/romanize
            return s.jpname
        return s.name
    
    def album_name(self, a):
        if a.jpname:
            return a.jpname
        return a.name

    @commands.command(name='song', help='gives info on song by id')
    async def song(self, ctx, sid):
        s = await models.D4DJSong.get_or_none(id=sid)
        if s:
            infoEmbed = discord.Embed(title=self.song_name(s))
            if s.album_id:
                a = await s.album.first()
                infoEmbed.add_field(name='Album', value=a.name)
            infoEmbed.add_field(name='Main Artists', value=process_artist(s.artist), inline=False)
            infoEmbed.add_field(name='Length', value=f'{s.length//60}:{s.length%60}', inline=False)
            asyncio.ensure_future(run_paged_message(ctx, [infoEmbed]))
        else:
            await ctx.send('song id not found')

    @commands.command(name='album', help='gives info on album by id')
    async def album(self, ctx, aid):
        a = await models.D4DJAlbum.get_or_none(id=aid)
        if a:
            await a.fetch_related('songs')
            songlist = []
            for s in a.songs:
                songlist.append(f'`{self.song_name(s)}`')
            infoEmbed = discord.Embed(title=self.album_name(a))
            infoEmbed.add_field(name='Track Listing', value='\n'.join(songlist))
            asyncio.ensure_future(run_paged_message(ctx, [infoEmbed]))
        else:
            await ctx.send('album id not found')


# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Music(bot))