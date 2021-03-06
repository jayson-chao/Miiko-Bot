# event.py
# commands for event cog, related to retrieving info on events

import asyncio
import discord
from datetime import datetime
import pytz
import re
from discord.ext import commands
from enum import IntEnum
from tortoise.query_utils import Q
from fuzzywuzzy import process, fuzz

from bot import MiikoBot
import models
from common.react_msg import run_paged_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists, media_name
from main import CMD_PREFIX

PAGE_SIZE = 15

event_aliases = { 
    'first': '1st',
    'second': '2nd',
    'night': 'evening'
}

class EventType(IntEnum):
    MAIN = 1
    DJTIME = 2
    STREAM = 3
    OTHER = 4

    ALL = 0

class Event(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    # returns array of relevant events
    async def match_events(self, args: ParsedArguments, type: EventType=None, future=True):
        events = models.D4DJEvent.all()
        if type and type != EventType.ALL:
            events = events.filter(Q(id__lt=type*1000) & Q(id__gt=(type-1)*1000))
        if 'all' in args.tags:
            return await events
        for tag in args.tags:
            if tag.isdigit():
                events = events.filter(id=tag)
            elif tag in unit_aliases:
                events = events.filter(artist__name=artists[unit_aliases[tag]])
            else: # bad tag - give empty
                return []
        if not future:
            now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d')
            events = events.filter(eventdate__lte=now)
        for word in args.words:
            if word in event_aliases: # manually catch some possible conversion/matching problems
                events = events.filter(Q(name__icontains=word) | Q(name__icontains=event_aliases[word]))
            else:
                if type == EventType.DJTIME or type == EventType.ALL:
                    events = events.filter(Q(artist__name__icontains=word) | Q(artist__jpname__icontains=word) | Q(name__icontains=word)).distinct()
                else:
                    events = events.filter(name__icontains=word)
        return await events.order_by("eventdate")

    @commands.command(name='event', 
                      help=f'{CMD_PREFIX}event d4 fes',
                      description='Shows a pageable embed of events in chronological order. Embed will start on the page of the closest upcoming event if there is one, otherwise the most recent event.\n\n'
                                  'Giving keyword arguments filters the pages down to events that include the given keywords in their names.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter events by artists)\n'
                                  '- $[event ID] (gives only the event with the matching internal ID)')
    async def get_event(self, ctx, *, args=None):
        # parse args into most relevant event based on tags/args, else get next event
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments, EventType.MAIN) 
        else:
            events = await models.D4DJEvent.filter(id__lt=1000).order_by("eventdate")
        
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        # make array of embeds
        if len(events) > 0:
            index = 0
            embeds = []
            for i, e in enumerate(events):
                infoEmbed = discord.Embed(title=e.name)
                if len(events) > 1:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}')
                else:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}')
                infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/event/{e.id}.png')
                e_time = pytz.timezone('Asia/Tokyo').localize(datetime.strptime(e.eventdate, '%Y-%m-%dT%H:%M:%S'))
                now = datetime.now(pytz.timezone('Asia/Tokyo'))
                if e_time > now:
                    delta = e_time - now
                    timestr = e_time.strftime('%Y-%m-%d @ %H:%M JST') + f'\nIn: {delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m'
                    infoEmbed.add_field(name='Event Date', value=timestr)
                    livestr = 'Unconfirmed'
                    if e.livestream:
                        livestr = e.livestream
                    infoEmbed.add_field(name='Livestream', value=livestr)
                else:
                    index += 1
                    infoEmbed.add_field(name='Event Date', value=e_time.strftime('%Y-%m-%d @ %H:%M JST'))
                    archivestr = 'None'
                    if e.archive: 
                        archivestr = e.archive
                    infoEmbed.add_field(name='Archive', value=archivestr)
                await e.fetch_related('artist')
                a = [await media_name(art, g.langpref) for art in e.artist]
                infoEmbed.add_field(name='Main Artists', value=', '.join(a), inline=False)
                if e.guests:
                    infoEmbed.add_field(name='Guests', value=e.guests)
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds, start=index))
        else:
            await ctx.send('No relevant events found.')

    @commands.command(name='events',
                      help=f'{CMD_PREFIX}events d4 fes',
                      description='Shows a paged list of events in chronological order.\n\n'
                                  'Giving keyword arguments filters the list down to events that include the given keywords in their names.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[artist] (to filter events by artists)')
    async def event_list(self, ctx, *, args=None): # plan to add list filtering based off of unit keyword later
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments, EventType.MAIN)
        else:
            events = await models.D4DJEvent.filter(id__lt=1000).order_by("eventdate")
        if len(events) < 1:
            await ctx.send('No relevant events found.')
            return

        eventlist = []
        for i, e in enumerate(events):
            if e.embedname:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.embedname}`')
            else:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.name}`')

        page_contents = [eventlist[i:i + PAGE_SIZE] for i in range(0, len(eventlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Events', description='\n'.join((e for e in page))) for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

    @commands.command(name='djtime',
                      help=f'{CMD_PREFIX}djtime tsunko',
                      description='Shows a pageable embed of DJTIME streams in chronological order. Embed will start on the page of the closest upcoming stream if there is one, otherwise the most recent stream.\n\n'
                                  'Giving keyword arguments filters the pages down to streams with keywords in their name/performers that match keywords.\n\n'
                                  'Useful $tag arguments include:\n'
                                  '- $[event ID] (gives only the event with the matching internal ID)')
    async def djtime(self, ctx, *, args=None):
         # parse args into most relevant event based on tags/args, else get next event
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments, EventType.DJTIME) 
        else:
            events = await models.D4DJEvent.filter(Q(id__lt=2000) & Q(id__gt=1000)).order_by("eventdate")
        
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        # make array of embeds
        if len(events) > 0:
            index = 0
            embeds = []
            for i, e in enumerate(events):
                infoEmbed = discord.Embed(title=e.name)
                if len(events) > 1:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}')
                else:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}')
                infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/event/{e.id}.png')
                e_time = pytz.timezone('Asia/Tokyo').localize(datetime.strptime(e.eventdate, '%Y-%m-%dT%H:%M:%S'))
                now = datetime.now(pytz.timezone('Asia/Tokyo'))
                if e_time > now:
                    delta = e_time - now
                    timestr = e_time.strftime('%Y-%m-%d @ %H:%M JST') + f'\nIn: {delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m'
                    infoEmbed.add_field(name='Stream Date', value=timestr)
                    livestr = 'No Link Available'
                    if e.livestream:
                        livestr = e.livestream
                    infoEmbed.add_field(name='Livestream', value=livestr)
                else:
                    index += 1
                    infoEmbed.add_field(name='Stream Date', value=e_time.strftime('%Y-%m-%d @ %H:%M JST'))
                    infoEmbed.add_field(name='Archive', value='[DJTIME Archive Folder](https://drive.google.com/drive/folders/11w4c10v7hRtsmJgpIvpxF3M2oGBzsdNk?usp=sharing)')
                await e.fetch_related('artist')
                a = [await media_name(art, g.langpref) for art in e.artist]
                infoEmbed.add_field(name='Performers', value=', '.join(a), inline=False)
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds, start=index))
        else:
            await ctx.send('No relevant events found.')

    @commands.command(name='djtimes',
                      help=f'{CMD_PREFIX}djtimes tsunko',
                      description='Shows a pageable list of DJTIME streams in chronological order.\n\n'
                                  'Giving keyword arguments filters the list down to streams with keywords in their name/performers that match keywords.')
    async def djtime_list(self, ctx, *, args=None): # plan to add list filtering based off of unit keyword later
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments, EventType.DJTIME)
        else:
            events = await models.D4DJEvent.filter(Q(id__gt=1000) & Q(id__lt=2000)).order_by("eventdate")
        if len(events) < 1:
            await ctx.send('No relevant events found.')
            return

        eventlist = []
        for i, e in enumerate(events):
            if e.embedname:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.embedname}`')
            else:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.name}`')
        page_contents = [eventlist[i:i + PAGE_SIZE] for i in range(0, len(eventlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Events', description='\n'.join((e for e in page))) for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

    @commands.command('setlist',
                      help=f'{CMD_PREFIX}setlist d4 fes',
                      description='Shows a pageable embed of setlists in chronological order starting from earliest event/DJTIME stream.\n\n'
                                  'Giving keyword arguments filters the pages down to events with keywords in their name/performers that match keywords (for DJTIME streams).\n\n'
                                  'Valid $tag arguments include:\n'
                                  '- $[artist] (to filter events by artists)\n'
                                  '- $[event ID] (gives only the event with the matching internal ID)')
    async def setlist(self, ctx, *, args=None):
        if args:
            events = await self.match_events(parse_arguments(args), EventType.ALL, future=False) 
        else:
            now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d')
            events = await models.D4DJEvent.all().filter(eventdate__lte=now).order_by("eventdate")
        if len(events) < 1:
            await ctx.send('No relevant events found.')
            return
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        embeds = []
        for i, e in enumerate(events):
            songs = await models.D4DJSetlist.filter(event=e).order_by("position") 
            setlistEmbed = discord.Embed(title=e.name)
            if len(events) > 1:
                setlistEmbed.set_footer(text=f'Event ID: {e.id}')
            if len(songs) < 1: # skip any events w/o setlists
                setlistEmbed.description = '`No setlist available.`'
                embeds.append(setlistEmbed)
                continue
            songlist = []
            counter = 1
            for s in songs:
                song = await s.song
                if song.id > 100000:
                    songlist.append(f'`     {await media_name(song, g.langpref)}`')
                elif song.id > 92000 and song.id < 95000:
                    songlist.append(f'`{counter}.{" " * (4-len(str(counter)))}{await media_name(song, g.langpref)} (Original)`')
                    counter += 1
                else:
                    songlist.append(f'`{counter}.{" " * (4-len(str(counter)))}{await media_name(song, g.langpref)}`')
                    counter += 1
            setlistEmbed.description = '\n'.join(songlist)
            embeds.append(setlistEmbed)
        asyncio.ensure_future(run_paged_message(ctx, embeds))

def setup(bot):
    bot.add_cog(Event(bot))
