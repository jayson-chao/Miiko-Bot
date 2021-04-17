# event.py
# commands for event cog, related to retrieving info on events

import asyncio
import discord
from datetime import datetime
import pytz
import re
from discord.ext import commands
from tortoise.queryset import QuerySet
from tortoise.query_utils import Q

from bot import MiikoBot
import models
from common.react_msg import run_paged_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists

event_aliases = { 
    'first': '1st',
    'second': '2nd',
    'night': 'evening'
}

class Event(commands.Cog):
    bot: MiikoBot

    def process_artist(self, a: str) -> str:
        perf_a = []
        for i, artist in enumerate(a):
            perf_a.append(artists[i])
        return ', '.join(perf_a)

    # returns array of relevant events
    async def match_events(self, args: ParsedArguments):
        if args.text.isdigit():
            return [await models.D4DJEvent.get_or_none(id=int(args.text))]
        else:
            events = models.D4DJEvent.all().order_by('id')
            for word in args.words: # if any word doesn't match, will return empty query
                if word in unit_aliases:
                    events = events.filter(artist__contains=str(unit_aliases[word]))
                elif word in event_aliases: # manually catch some possible conversion/matching problems
                    events = events.filter(Q(name__icontains=word) | Q(name__icontains=event_aliases[word]))
                else:
                    events = events.filter(name__icontains=word)

            return await events

    @commands.command(name='event', help='&event [id] to get event by id, &event [keywords] to filter by artist/live name')
    async def get_event(self, ctx, *, args=None):
        # parse args into most relevant event based on tags/args, else get next event
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments) 
        else:
            events = await models.D4DJEvent.all()
        
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
                if e.logo: # logos are just pulled from online right now, will need to go through and standardize format later
                    infoEmbed.set_thumbnail(url=e.logo)
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
                infoEmbed.add_field(name='Main Artists', value=self.process_artist(e.artist), inline=False)
                if e.guests:
                    infoEmbed.add_field(name='Guests', value=e.guests)
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds, start=index))
        else:
            await ctx.send('No relevant events found, nano!')

    @commands.command(name='events', help='get list of events ordered by id, &events [artist] to filter by artist')
    async def event_list(self, ctx, *, args=None): # plan to add list filtering based off of unit keyword later
        if args:
            arguments = parse_arguments(args)
            events = await self.match_events(arguments)
        else:
            events = await models.D4DJEvent.all()

        eventlist = []
        for e in events:
            if e.embedname:
                eventlist.append(f'`{e.id}.{" " * (5-len(str(e.id)))}{e.embedname}`')
            else:
                eventlist.append(f'`{e.id}.{" " * (5-len(str(e.id)))}{e.name}`')

        PAGE_SIZE = 10 # defining here temporarily, can make a preference
        page_contents = [eventlist[i:i + PAGE_SIZE] for i in range(0, len(eventlist), PAGE_SIZE)]
        embeds = [discord.Embed(title='Events', description=f'`ID    EVENT`\n'+'\n'.join((e for e in page))).set_footer(text=f'Page {str(i+1)}/{len(page_contents)}') for i, page in enumerate(page_contents)]
        
        asyncio.ensure_future(run_paged_message(ctx, embeds))

def setup(bot):
    bot.add_cog(Event(bot))
