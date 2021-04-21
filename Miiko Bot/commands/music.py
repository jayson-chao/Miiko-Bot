# music.py
# music commands for bot

from queue import SimpleQueue
import asyncio
import discord
from discord.ext import commands
from discord import ClientException
from tortoise.query_utils import Q

import models
from bot import MiikoBot
from common.react_msg import run_paged_message, run_swap_message
from common.parse_args import ParsedArguments, parse_arguments
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

    @commands.command(name='join', help='has Miiko join user\'s voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            raise VoiceError('You are not connected to a voice channel')
        if ctx.guild.id not in self.bot.player: # reset queue if there is none
            self.bot.player[ctx.guild.id] = SimpleQueue()
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
            await ctx.send("Connected!")
            return
        if ctx.voice_client.channel is not channel:
            await ctx.voice_client.move_to(channel)
            await ctx.send("Moved channels!")

    @commands.command(name='leave', aliases=['disconnect', 'dc'], help='has Miiko leave voice channel')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('leave: Bot is not connected to any voice channel')
        self.bot.player[ctx.guild.id] = SimpleQueue()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected!')

    # currently plays though to end, does not allow more play commands
    @commands.command(name='play', hidden=True, help='play song')
    async def play(self, ctx, id=None):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('play: Bot is not connected to any voice channel')
        if ctx.voice_client.is_paused() and not id:
            ctx.voice_client.resume()
            return
        # need a none check against audio
        self.bot.player[ctx.guild.id].put((id, discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=f'https://github.com/jayson-chao/Miiko-Bot/blob/master/Miiko%20Bot/common/assets/music/{id}.mp3?raw=true')))
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await ctx.send(f'{id} placed in song queue')
        else:
            self.play_next(ctx)

    def play_next(self, ctx):
        if not ctx.voice_client: 
            return # disconnect handles stop()
        if self.bot.player[ctx.guild.id].empty():
            ctx.voice_client.stop() # need to stop for good - was running into glitch where if queue stopped then refilled, the first added song would trip an error
            asyncio.run_coroutine_threadsafe(ctx.send("Queue finished!"), self.bot.loop)
            return
        next_song = self.bot.player[ctx.guild.id].get()
        asyncio.run_coroutine_threadsafe(ctx.send(f'Now playing {next_song[0]}'), self.bot.loop)
        self.bot.playing[ctx.guild.id] = next_song[0]
        ctx.voice_client.play(next_song[1], after=lambda e:self.play_next(ctx))

    @commands.command(name='skip', hidden=True, help='skip the current song')
    async def skip(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop() # don't need play_next, stop() will trigger vc.play.after

    @commands.command(name='pause', hidden=True, help='pause the song')
    async def pause(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(name='stop', hidden=True, help='stop playing song')
    async def stop(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('stop: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing():
            self.bot.player[ctx.guild.id] = SimpleQueue() # empty queue before triggering vc.play.after
            ctx.voice_client.stop()

    @commands.command(name='np', aliases=['nowplaying'], hidden=True, help='display info for current song')
    async def now_playing(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.send(f'PLAYING: {self.bot.playing[ctx.guild.id]}')
        else:
            await ctx.send('Not playing anything!')

    def media_name(self, a): # album & song have same name fields in model
        if a.jpname:
            return a.jpname
        return a.name

    async def match_songs(self, args: ParsedArguments):
        if args.text.isdigit():
            return[await models.D4DJSong.get_or_none(id=int(args.text))]
        else:
            songs = models.D4DJSong.all().order_by('id')
            for word in args.words:
                if word in unit_aliases:
                    songs = songs.filter(artist__contains=str(unit_aliases[word]))
                else:
                    songs = songs.filter(Q(name__icontains=word)|Q(jpname__icontains=word)|Q(romanizedname__icontains=word))
            return await songs

    async def match_albums(self, args: ParsedArguments):
        if args.text.isdigit():
            return[await models.D4DJAlbum.get_or_none(id=int(args.text))]
        else:
            albums = models.D4DJAlbum.all().order_by('id')
            for word in args.words:
                if word in unit_aliases:
                    albums = albums.filter(artist__contains=str(unit_aliases[word]))
                else:
                    albums = albums.filter(Q(name__icontains=word)|Q(jpname__icontains=word)|Q(romanizedname__icontains=word))
            return await albums

    @commands.command(name='song', help='gives info on song based off search terms')
    async def song(self, ctx, *, args=None):
        if not args:
            await ctx.send('No relevant songs found')
            return
        arguments = parse_arguments(args)
        songs = await self.match_songs(arguments)
        if len(songs) > 0:
            embeds = []
            for i, s in enumerate(songs):
                infoEmbed = discord.Embed(title=self.media_name(s))
                if len(songs) > 1:
                    infoEmbed.set_footer(text=f'Page {i+1}/{len(songs)}')
                if s.album:
                    a = await s.album.first()
                    infoEmbed.add_field(name='Album', value=self.media_name(a))
                    infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Bot/master/Miiko%20Bot/common/assets/album/{a.id:03d}.png')
                infoEmbed.add_field(name='Artist(s)', value=process_artist(s.artist), inline=False)
                if s.length:
                    infoEmbed.add_field(name='Length', value=f'{s.length//60}:{s.length%60:02d}', inline=False)
                infoEmbed.add_field(name='Type', value=('Original' if s.original else 'Cover'))
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds))
        else:
            await ctx.send('No relevant songs found')

    @commands.command(name='album', help='gives info on album based off search terms')
    async def album(self, ctx, *, args=None):
        if not args:
            await ctx.send('No relevant albums found')
            return
        arguments = parse_arguments(args)
        albums = await self.match_albums(arguments)
        if len(albums) > 0:
            albumembeds = []
            tracklistings = [] # plan is to have button to swap between album basic info/track listing
            for i, a in enumerate(albums):
                await a.fetch_related('songs')
                songlist = []
                for j, s in enumerate(await a.songs.order_by('track')):
                    songlist.append(f'`{j+1}.{" " * (4-len(str(j)))}{self.media_name(s)}`')
                albumEmbed = discord.Embed(title=self.media_name(a))
                albumEmbed.add_field(name='Artist(s)', value=(a.artiststr if a.artiststr else process_artist(a.artist)), inline=False)
                albumEmbed.add_field(name='Release Date', value=a.releasedate)
                trackEmbed = discord.Embed(title=self.media_name(a))
                trackEmbed.add_field(name='Track Listing', value='\n'.join(songlist))
                if len(albums) > 1:
                    albumEmbed.set_footer(text=f'Page {i+1}/{len(albums)}')
                    trackEmbed.set_footer(text=f'Page {i+1}/{len(albums)}')
                albumEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Bot/master/Miiko%20Bot/common/assets/album/{a.id:03d}.png')
                trackEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Bot/master/Miiko%20Bot/common/assets/album/{a.id:03d}.png')
                albumembeds.append(albumEmbed)
                tracklistings.append(trackEmbed)
            asyncio.ensure_future(run_swap_message(ctx, [albumembeds, tracklistings]))
        else:
            await ctx.send('No relevant albums found')


# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Music(bot))