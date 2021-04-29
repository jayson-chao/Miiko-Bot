# event.py
# commands for event cog, related to retrieving info on events

import asyncio
import discord
from datetime import datetime
import pytz
import re
from discord.ext import commands
from tortoise.query_utils import Q

from bot import MiikoBot
import models
from common.react_msg import run_paged_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists, process_artist

event_aliases = { 
    'first': '1st',
    'second': '2nd',
    'night': 'evening'
}

class Event(commands.Cog):
    bot: MiikoBot

    # returns array of relevant events
    async def match_events(self, args: ParsedArguments):
        events = models.D4DJEvent.all().filter(id__lt=1000)
        if 'all' in args.tags:
            return await events
        for tag in args.tags:
            if tag.isdigit():
                events = events.filter(id=tag)
            elif tag in unit_aliases:
                events = events.filter(artist__contains=str(unit_aliases[tag]))
            else: # bad tag - give empty
                return []
        for word in args.words:
            if word in event_aliases: # manually catch some possible conversion/matching problems
                events = events.filter(Q(name__icontains=word) | Q(name__icontains=event_aliases[word]))
            else:
                events = events.filter(name__icontains=word)
        return await events

    @commands.command(name='event', help='&event [terms | $tags], shows event info')
    async def get_event(self, ctx, *, args=None):
        # parse args into most relevant event based on tags/args, else get next event
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments) 
        else:
            events = await models.D4DJEvent.all()
        
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        # make array of embeds
        if len(events) > 0:
            index = 0
            embeds = []
            for i, e in enumerate(events):
                infoEmbed = discord.Embed(title=e.name)
                if len(events) > 1:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}\nPage {i+1}/{len(events)}')
                else:
                    infoEmbed.set_footer(text=f'Event ID: {e.id}')
                infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Bot/master/Miiko%20Bot/common/assets/event/{e.id}.png')
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
                infoEmbed.add_field(name='Main Artists', value=process_artist(e.artist, g.langpref), inline=False)
                if e.guests:
                    infoEmbed.add_field(name='Guests', value=e.guests)
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds, start=index))
        else:
            await ctx.send('No relevant events found.')

    @commands.command(name='events', help='&events [terms | $tags], lists events')
    async def event_list(self, ctx, *, args=None): # plan to add list filtering based off of unit keyword later
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments)
        else:
            events = await models.D4DJEvent.filter(id__lt=1000)
        if len(events) < 1:
            await ctx.send('No relevant events found.')
            return

        eventlist = []
        for i, e in enumerate(events):
            if e.embedname:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.embedname}`')
            else:
                eventlist.append(f'`{i+1}.{" " * (5-len(str(i+1)))}{e.name}`')
        PAGE_SIZE = 10 # defining here temporarily, can make a preference
        page_contents = [eventlist[i:i + PAGE_SIZE] for i in range(0, len(eventlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Events', description='\n'.join((e for e in page))).set_footer(text=f'Page {str(i+1)}/{len(page_contents)}') for i, page in enumerate(page_contents)]
        asyncio.ensure_future(run_paged_message(ctx, embeds))

def setup(bot):
    bot.add_cog(Event(bot))
