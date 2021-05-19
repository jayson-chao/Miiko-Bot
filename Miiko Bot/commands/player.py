# player.py
# music player commands

from queue import Queue
import asyncio
import discord
import requests
from discord.ext import commands
from discord import ClientException
from tortoise.query_utils import Q
from fuzzywuzzy import process

import models
from bot import MiikoBot
from common.react_msg import run_paged_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists, process_artist, LangPref, media_name

PAGE_SIZE=15

class Player(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='join user\'s vc')
    async def join(self, ctx):
        if not ctx.author.voice:
            raise VoiceError('You are not connected to a voice channel.')
        if ctx.guild.id not in self.bot.player: # reset queue if there is none
            self.bot.player[ctx.guild.id] = Queue()
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
            await ctx.send("Connected!")
            return
        if ctx.voice_client.channel is not channel:
            await ctx.voice_client.move_to(channel)
            await ctx.send("Moved channels!")

    @commands.command(name='leave', aliases=['disconnect', 'dc'], help='leave current vc')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('leave: Bot is not connected to any voice channel')
        self.bot.player[ctx.guild.id] = Queue()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected!')

    # unlike match_songs for embeds, has to pick a single song to play 
    async def choose_song(self, args: ParsedArguments):
        songs = models.D4DJSong.all().filter(id__lt=92000)
        for tag in args.tags: # no $all tag since need a single result
            if tag.isdigit():
                media = media.filter(id=tag)
            elif tag in unit_aliases:
                media = media.filter(artist__contains=str(unit_aliases[tag]))
            else: # bad tag - give empty
                return None
        for word in args.words:
            songs = songs.filter(Q(name__icontains=word)|Q(jpname__icontains=word)|Q(roname__icontains=word))
        songs = await songs.values_list('name', 'jpname', 'roname', 'id')
        best = (-1, -1)
        for n, j, r, i in songs:
            ratio = process.extractOne(args.text, [n, j, r])
            if ratio[1] > best[1]:
                best = (i, ratio[1])
        return best[0]

    @commands.command(name='play', help='&play [terms | $tags] to queue most relevant song, &play to resume')
    async def play(self, ctx, *, args=None):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('play: Bot is not connected to any voice channel')
        if ctx.voice_client.is_paused() and not args:
            ctx.voice_client.resume()
            return
        arguments = parse_arguments(args)
        id = await self.choose_song(arguments)
        if id is None or id < 0:
            await ctx.send('No relevant song found.')
            return

        song = await models.D4DJSong.get_or_none(id=id)
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        
        # check that asset address responds w/o error
        r = requests.head(f'https://github.com/jayson-chao/Miiko-Assets/blob/main/music/{id:05d}.mp3?raw=true')
        if not r:
            await ctx.send(f'{await media_name(song, g.langpref)} is not available at the moment.')
            return

        self.bot.player[ctx.guild.id].put((song, discord.FFmpegPCMAudio(source=f'https://github.com/jayson-chao/Miiko-Assets/blob/main/music/{id:05d}.mp3?raw=true')))
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await ctx.send(f'{await media_name(song, g.langpref)} placed in song queue')
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
        asyncio.run_coroutine_threadsafe(self.up_next(ctx, next_song[0]), self.bot.loop) # will need to make function to replace this - this queue method doesn't change name w/ langpref change
        self.bot.playing[ctx.guild.id] = next_song[0]
        ctx.voice_client.play(next_song[1], after=lambda e:self.play_next(ctx))

    async def up_next(self, ctx, song):
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        await ctx.send(f'Now playing {await media_name(song, g.langpref)}')

    @commands.command(name='skip', help='skip current song')
    async def skip(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop() # don't need play_next, stop() will trigger vc.play.after

    @commands.command(name='pause', help='pause player')
    async def pause(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('pause: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(name='stop', help='stop player, empty queue')
    async def stop(self, ctx):
        if not ctx.voice_client:
            await ctx.send('Not connected to any voice channel!')
            raise VoiceError('stop: Bot is not connected to any voice channel')
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            self.bot.player[ctx.guild.id] = Queue() # empty queue before triggering vc.play.after
            ctx.voice_client.stop()

    @commands.command(name='np', aliases=['nowplaying'], help='display info for current song')
    async def now_playing(self, ctx):
        if ctx.voice_client.is_playing():
            g = await models.Guild.get_or_none(id=ctx.guild.id)
            s = self.bot.playing[ctx.guild.id]
            infoEmbed = discord.Embed(title=await media_name(s, g.langpref))
            if s.album:
                a = await s.album.first()
                infoEmbed.add_field(name='Album', value=await media_name(a, g.langpref))
                infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Bot/master/Miiko%20Bot/common/assets/album/{a.id:03d}.png')
            infoEmbed.add_field(name='Artist(s)', value=(await media_name(await s.artiststr.first(), g.langpref) if s.artiststr else process_artist(s.artist, g.langpref)), inline=False)
            if s.length:
                infoEmbed.add_field(name='Length', value=f'{s.length//60}:{s.length%60:02d}', inline=False)
            infoEmbed.add_field(name='Type', value=(f'Cover ({await media_name(await s.orartist.first(), g.langpref)})' if s.orartist else 'Original'))
            asyncio.ensure_future(run_paged_message(ctx, [infoEmbed]))
        else:
            await ctx.send('Not playing anything!')

    @commands.command(name='queue', aliases=['nextup'], help='show currently queued songs')
    async def show_queue(self, ctx):
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            g = await models.Guild.get_or_none(id=ctx.guild.id)
            songlist = []
            cur = self.bot.playing[ctx.guild.id]
            songlist.append(f'`NP.   {await media_name(cur, g.langpref)}`')
            for i, s in enumerate(list(self.bot.player[ctx.guild.id].queue)):
                songlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{await media_name(s[0], g.langpref)}`')
            page_contents = [songlist[i:i + PAGE_SIZE] for i in range(0, len(songlist), PAGE_SIZE)]
            embeds = [discord.Embed(title='Play Queue', description='\n'.join((e for e in page))) for i, page in enumerate(page_contents)]
            asyncio.ensure_future(run_paged_message(ctx, embeds))
        else:
            await ctx.send('Not playing anything!')

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Player(bot))
