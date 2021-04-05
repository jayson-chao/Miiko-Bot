# event.py
# commands for event cog, related to retrieving info on events

import discord
from discord.ext import commands

from bot import MiikoBot
import models

class Event(commands.Cog):
    bot: MiikoBot

    @commands.command(name='event', help='get event based off id (name matching coming later)')
    async def event(self, ctx, eid): # fuzzy matching/aliases coming later
        e = await models.D4DJEvent.get_or_none(id=eid)
        if e:
            infoEmbed = discord.Embed(title=e.name)
            infoEmbed.add_field(name='Event Date', value=e.eventdate)
            archivestr = 'None'
            if e.logo: # logos are just pulled from online right now, will need to go through and standardize format later
                infoEmbed.set_thumbnail(url=e.logo)
            if e.archive:
                archivestr = '[Link](' + e.archive + ')'
            infoEmbed.add_field(name='Archive', value=archivestr)
            await ctx.send(embed=infoEmbed)
        else:
            await ctx.send('Invalid Event ID, nano!')

def setup(bot):
    bot.add_cog(Event(bot))
