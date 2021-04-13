# react_msg.py
# functions to run messages with reaction-based commands

import asyncio
import discord
from discord.ext.commands import Context

# assumes page content was already sorted out beforehand
async def run_paged_message(ctx: Context, embed_pages, *, start=0):
    index = min(start, len(embed_pages)-1)
    message = await ctx.send(embed=embed_pages[index])
    
    double_left_arrow = '⏪'
    double_right_arrow = '⏩'
    left_arrow = '◀'
    right_arrow = '▶'
    delete = '❎'
    page_emojis = [double_left_arrow, left_arrow, right_arrow, double_right_arrow]
    emojis = []

    # quick fix for if embed only has single page
    if len(embed_pages) > 1:
        for e in page_emojis:
            emojis.append(e)
            await message.add_reaction(e)
    await message.add_reaction(delete)
    emojis.append(delete)

    def check(react, user):
        return user == ctx.author and react.emoji in emojis and react.message.id == message.id

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=600, check=check)
            if reaction.emoji == delete:
                await message.delete()
                return
            
            new_index = index
            # don't need to do if statement on emoji here bc wait_for check automatically checks 
            if reaction.emoji == double_left_arrow:
                new_index = 0
            elif reaction.emoji == left_arrow:
                new_index -= 1
            elif reaction.emoji == right_arrow:
                new_index += 1
            elif reaction.emoji == double_right_arrow:
                new_index = len(embed_pages) - 1
            new_index = min(len(embed_pages) - 1, max(0, new_index))

            if new_index != index:
                index = new_index
                await message.edit(embed=embed_pages[index])

            await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            for e in emojis:
                await message.remove_reaction(e, ctx.bot.user)
            break