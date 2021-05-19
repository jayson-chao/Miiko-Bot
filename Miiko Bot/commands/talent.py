# talent.py
# seiyuu-related commands

import asyncio
import discord
from discord.ext import commands
from tortoise import Tortoise
from tortoise.query_utils import Q
from fuzzywuzzy import process
from datetime import datetime
import pytz

from bot import MiikoBot
import models
from common.react_msg import run_paged_message
from common.parse_args import ParsedArguments, parse_arguments
from common.aliases import unit_aliases, artists, process_artist, LangPref, media_name

class Talent(commands.Cog):
    bot: MiikoBot

    def __init__(self, bot):
        self.bot = bot

    async def match_seiyuu(self, args: ParsedArguments):
        seiyuu = models.D4DJSeiyuu.all()
        if 'all' in args.tags:
            return await seiyuu
        for tag in args.tags:
            # planned tags - unit, agency
            # else: # bad tag - give empty
            return []
        for word in args.words:
            seiyuu = seiyuu.filter(Q(name__icontains=word) | Q(jpname__icontains=word))
        return await seiyuu

    @commands.command(name='seiyuu', help='seiyuu embed [WIP]', hidden=True)
    async def seiyuu(self, ctx, *, args=None):
        if args:
            arguments = parse_arguments(args)
            seiyuu = await self.match_seiyuu(arguments) 
        else:
            seiyuu = await models.D4DJSeiyuu.all()
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        # make array of embeds
        if len(seiyuu) > 0:
            index = 0
            embeds = []
            for i, s in enumerate(seiyuu):
                infoEmbed = discord.Embed(title=await media_name(s, g.langpref))
                infoEmbed.set_thumbnail(url=f'https://raw.githubusercontent.com/jayson-chao/Miiko-Assets/main/seiyuu/{s.id}.png')
                infoEmbed.add_field(name="Birth Date", value=s.birthday)
                embeds.append(infoEmbed)
            asyncio.ensure_future(run_paged_message(ctx, embeds, start=index))
        else:
            await ctx.send('No relevant seiyuu found.')

    @commands.command(name="birthday", aliases=["bday"], help="birthday list [WIP]", hidden=True)
    async def birthday(self, ctx, *, args=None):
        g = await models.Guild.get_or_none(id=ctx.guild.id)
        if args:
            if args.lower() == "next":
                now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%m-%d')
                seiyuu = models.D4DJSeiyuu.all().order_by('birthday')
                c = await seiyuu.first() # in case current date is beyond all birthdays in jan-dec timeline
                async for s in seiyuu:
                    if now < s.birthday:
                        c = s
                        break
                bdayEmbed = discord.Embed(title="Seiyuu Birthdays", description=f'{await media_name(s, g.langpref)} - {s.birthday[:5]}')
                asyncio.ensure_future(run_paged_message(ctx, [bdayEmbed]))
            else:
                await ctx.send('invalid arg')

        else:
            bdayEmbed = discord.Embed(title="Seiyuu Birthdays")
            b = []
            async for s in models.D4DJSeiyuu.all().order_by('birthday'):
                b.append(f'`{s.birthday[:5]}  {await media_name(s, g.langpref)}`')
            bdayEmbed.description = '\n'.join(b)
            asyncio.ensure_future(run_paged_message(ctx, [bdayEmbed]))

# expected by load_extension in bot
def setup(bot):
    bot.add_cog(Talent(bot))