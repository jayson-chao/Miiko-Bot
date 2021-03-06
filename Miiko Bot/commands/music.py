# music.py
# music commands for bot

import asyncio
import discord
import requests
from discord.ext import commands
from discord import ClientException
from tortoise.query_utils import Q
from typing import Union
from fuzzywuzzy import process

import models
from bot import MiikoBot
from common.react_msg import run_paged_message, run_swap_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists, process_artist, LangPref, media_name, art_colors
from main import CMD_PREFIX

PAGE_SIZE=15

class VoiceError(Exception):
    pass

class Music (commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    async def match_media(self, args: ParsedArguments, media_type):
        media = media_type.all().order_by('id').filter(id__lt=92000) # in place for song id related reasons
        if 'all' in args.tags:
            return await media
        for tag in args.tags:
            if tag.isdigit():
                media = media.filter(id=tag)
            elif tag in unit_aliases:
                media = media.filter(artist__contains=str(unit_aliases[tag]))
            else: # bad tag - give empty
                return []
        for word in args.words:
                media = media.filter(Q(name__icontains=word)|Q(jpname__icontains=word)|Q(roname__icontains=word))
        return await media

    @commands.command(name='song',
                      help=f'{CMD_PREFIX}song guru guru',
                      description='Shows a pageable embed of songs, use rotate react to swap between info/staff listing. Requires keyword or $tag argument.\n\n'
                                  'Giving keyword arguments filters pages down to songs with keywords in title.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter songs by artists)\n'
                                  '- $all (returns pages for all original/cover songs)')
    async def song(self, ctx, *, args=None):
        if not args:
            await ctx.send('No relevant songs found.')
            return
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        arguments = parse_arguments(args)
        songs = await self.match_media(arguments, models.D4DJSong)
        if len(songs) > 0:
            infoembeds = []
            staffembeds = []
            for i, s in enumerate(songs):
                trackEmbed = discord.Embed(title=await media_name(s, g.langpref), color = art_colors[s.id // 10000])
                staffEmbed = discord.Embed(title=await media_name(s, g.langpref), color = art_colors[s.id // 10000])
                if s.album:
                    a = await s.album.first()
                    trackEmbed.add_field(name='Album', value=await media_name(a, g.langpref))
                    trackEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/album/{a.id:03d}.png')
                    staffEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/album/{a.id:03d}.png')
                trackEmbed.add_field(name='Artist(s)', value=(await media_name(await s.artiststr.first(), g.langpref) if s.artiststr else process_artist(s.artist, g.langpref)), inline=False)
                if s.length:
                    trackEmbed.add_field(name='Length', value=f'{s.length//60}:{s.length%60:02d}', inline=False)
                trackEmbed.add_field(name='Type', value=(f'Cover ({await media_name(await s.orartist.first(), g.langpref)})' if s.orartist else 'Original'))
                
                # massively increases embed load time. may move back to loading files locally/detecting if path exists so it speeds this up
                # r = requests.head(f'https://github.com/jayson-chao/Miiko-Assets/blob/main/music/{s.id:05d}.mp3?raw=true')
                # staffEmbed.add_field(name='Playable by Bot', value='Yes' if r else 'No', inline=False)

                await s.fetch_related('lyricist')
                if s.lyricist:
                    c = [await media_name(com, g.langpref) for com in s.lyricist]
                    staffEmbed.add_field(name='Lyricist(s)', value=', '.join(c), inline=False)
                await s.fetch_related('composer')
                if s.composer:
                    c = [await media_name(com, g.langpref) for com in s.composer]
                    staffEmbed.add_field(name='Composer(s)', value=', '.join(c), inline=False)
                await s.fetch_related('arranger')
                if s.arranger:
                    c = [await media_name(com, g.langpref) for com in s.arranger]
                    staffEmbed.add_field(name='Arranger(s)', value=', '.join(c), inline=False)

                infoembeds.append(trackEmbed)
                staffembeds.append(staffEmbed)
            asyncio.ensure_future(run_swap_message(ctx, [infoembeds, staffembeds]))
        else:
            await ctx.send('No relevant songs found.')

    @commands.command(name='songs',
                      help=f'{CMD_PREFIX}songs $rondo',
                      description='Shows a list of songs.\n\n'
                                  'Giving keyword arguments filters list down to songs with keywords in title.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter songs by artists)')
    async def list_songs(self, ctx, *, args=None):
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        if args:
            arguments = parse_arguments(args)
            songs = await self.match_media(arguments, models.D4DJSong)
        else:
            songs = await models.D4DJSong.all().filter(id__lt=92000)
        if len(songs) < 1:
            await ctx.send('No relevant songs found.')
            return

        songlist = []
        for i, s in enumerate(songs):
            if s.orartist:
                songlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{await media_name(s, g.langpref)} (Cover)`')
            else:
                songlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{await media_name(s, g.langpref)}`')
        page_contents = [songlist[i:i + PAGE_SIZE] for i in range(0, len(songlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Songs', description='\n'.join((e for e in page))) for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

    @commands.command(name='album',
                      help=f'{CMD_PREFIX}album cover',
                      description='Shows a pageable embed of albums, use rotate react to swap between info/tracklist. Requires keyword or $tag argument.\n\n'
                                  'Giving keyword arguments filters pages down to albums with keywords in title.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter albums by artists)')
    async def album(self, ctx, *, args=None):
        if not args:
            await ctx.send('No relevant albums found.')
            return
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        arguments = parse_arguments(args)
        albums = await self.match_media(arguments, models.D4DJAlbum)
        if len(albums) > 0:
            albumembeds = []
            tracklistings = [] # plan is to have button to swap between album basic info/track listing
            for i, a in enumerate(albums):
                await a.fetch_related('songs')
                songlist = []
                for j, s in enumerate(await a.songs.order_by('track')):
                    songlist.append(f'`{j+1}.{" " * (4-len(str(j)))}{await media_name(s, g.langpref)}`')
                albumtitle = await media_name(a, g.langpref)
                albumEmbed = discord.Embed(title=albumtitle, color = art_colors[a.id // 100])
                albumEmbed.add_field(name='Artist(s)', value=(await media_name(await a.artiststr.first(), g.langpref) if a.artiststr else process_artist(a.artist, g.langpref)), inline=False)
                albumEmbed.add_field(name='Release Date', value=a.releasedate)
                trackEmbed = discord.Embed(title=albumtitle, color = art_colors[a.id // 100])
                trackEmbed.add_field(name='Track Listing', value='\n'.join(songlist))
                albumEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/album/{a.id:03d}.png')
                trackEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/album/{a.id:03d}.png')
                albumembeds.append(albumEmbed)
                tracklistings.append(trackEmbed)
            asyncio.ensure_future(run_swap_message(ctx, [albumembeds, tracklistings]))
        else:
            await ctx.send('No relevant albums found.')

    @commands.command(name='albums',
                      help=f'{CMD_PREFIX}albums $rondo',
                      description='Shows a list of albums.\n\n'
                                  'Giving keyword arguments filters list down to albums with keywords in title.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter albums by artists)')
    async def list_albums(self, ctx, *, args=None):
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        if args:
            arguments = parse_arguments(args)
            albums = await self.match_media(arguments, models.D4DJAlbum())
        else:
            albums = await models.D4DJAlbum.all()
        if len(albums) < 1:
            await ctx.send('No relevant albums found.')
            return

        albumlist = []
        for i, a in enumerate(albums):
            albumlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{await media_name(a, g.langpref)}`')
        page_contents = [albumlist[i:i + PAGE_SIZE] for i in range(0, len(albumlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Albums', description='\n'.join((e for e in page))) for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

    async def match_staff(self, args: ParsedArguments):
        staff = models.D4DJStaff.all().order_by('name')
        if 'all' in args.tags:
            return await staff
        for tag in args.tags:
            return [] # no tag filters at the moment so any tag aside from 'all' returns empty set
        for word in args.words:
            staff = staff.filter(Q(name__icontains=word)|Q(jpname__icontains=word))
        names = await staff.values_list('name', 'jpname')
        best = (None, -1)
        for n, j in names:
            ratio = process.extractOne(args.text, [n, j])
            if ratio[1] > best[1]:
                best = (n, ratio[1])
        return best[0]

    @commands.command(name='staff',
                      help=f'{CMD_PREFIX}staff nakamura',
                      description='Shows a paged embed of relevant staff members, each with a list of songs they have worked on.\n\n'
                                  'Giving keyword arguments filters pages down to staff members with keywords in their name.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $all (returns pages for all staff that have worked on music)')
    async def list_staff(self, ctx, *, args=None):
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        if args:
            staff = await self.match_staff(parse_arguments(args))
        else:
            await ctx.send('No staff member found.')
            return

        s = await models.D4DJStaff.get_or_none(name=staff)
        songlist = []
        # filter on D4DJSong wasn't working properly, using union and sort while I look for quick fix while I look into the problem
        await s.fetch_related('lyricized')
        await s.fetch_related('composed')
        await s.fetch_related('arranged')
        songs = set((s.lyricized)).union(set(s.composed), set(s.arranged))
        for i, so in enumerate(sorted(songs, key=lambda x:x.id)):
            did = []
            if so in s.lyricized:
                did.append('L')
            if so in s.composed:
                did.append('C')
            if so in s.arranged:
                did.append('A')

            songlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{await media_name(so, g.langpref)} ({"".join(did)})`')

        page_contents = [songlist[i:i + PAGE_SIZE] for i in range(0, len(songlist), PAGE_SIZE)]
        embeds = [discord.Embed(title=await media_name(s, g.langpref), description='\n'.join((s for s in page))) for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Music(bot))