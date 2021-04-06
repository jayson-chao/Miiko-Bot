# event.py
# commands for event cog, related to retrieving info on events

import asyncio
import discord
from datetime import datetime
import pytz
import re
from discord.ext import commands
from tortoise.queryset import QuerySet

from bot import MiikoBot
import models
from commands.react_msg import run_paged_message

# move to some sort of Common folder later?
artists = ["Happy Around!", "Peaky P-key", "Photon Maiden", "Merm4id", "RONDO", "Lyrical Lily"]
def process_artist(a: str) -> str:
    pattern = re.compile('[01]{6}')
    if pattern.fullmatch(a):
        str = ""
        for i, artist in enumerate(a):
            if artist == '1':
                str = str + artists[i] + ', '
        return str[0:-2]
    raise ValueError

# to return a single instance of an event (might make paged? but sticking to simple stuff for now LOL)
def match_event(self, e_str: str):
    return

async def event_list():
    events = []
    async for e in models.D4DJEvent.all().order_by('id'):
        if e.embedname:
            events.append(f'`{e.id}.{" " * (4-len(str(e.id)))}{e.embedname}`')
        else:
            events.append(f'`{e.id}.{" " * (4-len(str(e.id)))}{e.name}`')
    return events

class Event(commands.Cog):
    bot: MiikoBot

    @commands.command(name='event', help='get event based off id (name matching coming later)')
    async def event(self, ctx, eid): # add name matching later
        # events = models.D4DJEvent.all() # manually filter by name i guess?
        e = await models.D4DJEvent.get_or_none(id=eid)
        if e:
            infoEmbed = discord.Embed(title=e.name)
            if e.logo: # logos are just pulled from online right now, will need to go through and standardize format later
                infoEmbed.set_thumbnail(url=e.logo)
            e_time = pytz.timezone('Asia/Tokyo').localize(datetime.strptime(e.eventdate, '%Y-%m-%dT%H:%M:%S'))
            now = datetime.now(pytz.timezone('Asia/Tokyo'))
            if e_time > now:
                delta = e_time - now
                timestr = e_time.strftime('%Y-%m-%d @ %H:%M JST') + f'\nIn: {delta.days}d {delta.seconds//3600}h {(delta.seconds//60)%60}m'
                infoEmbed.add_field(name='Event Date', value=timestr)
                livestr = 'Unconfirmed'
                if e.livestream: # don't know how to distiguish paid and free livestreams yet - might need separate fields
                    archivestr = '[Link](' + e.livestream + ')'
                infoEmbed.add_field(name='Livestream', value=livestr)
            else:
                infoEmbed.add_field(name='Event Date', value=e_time.strftime('%Y-%m-%d @ %H:%M JST'))
                archivestr = 'None'
                if e.archive: 
                    archivestr = '[Link](' + e.archive + ')' # might edit these strings to do the hyperlink directly in the db
                infoEmbed.add_field(name='Archive', value=archivestr)
            infoEmbed.add_field(name='Main Artists', value=process_artist(e.artist), inline=False)
            if e.guests:
                infoEmbed.add_field(name='Guests', value=e.guests)
            await ctx.send(embed=infoEmbed)
        else:
            await ctx.send('Invalid Event ID, nano!')

    @commands.command(name='events', help='get list of events, lists with id for now')
    async def event_list(self, ctx): # plan to add list filtering based off of unit keyword later
        events = await event_list()
        PAGE_SIZE = 10
        page_contents = [events[i:i + PAGE_SIZE] for i in range(0, len(events), PAGE_SIZE)]
        embeds = [discord.Embed(title='Events', description='\n'.join((e for e in page))).set_footer(text=f'Page {str(i+1)}/{len(page_contents)}') for i, page in enumerate(page_contents)]
        
        asyncio.ensure_future(run_paged_message(ctx, embeds))
        # await ctx.send('Work in progress, nano!')


def setup(bot):
    bot.add_cog(Event(bot))
