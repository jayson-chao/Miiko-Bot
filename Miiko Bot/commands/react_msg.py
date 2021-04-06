# react_msg.py
# functions to run messages with reaction-based commands

import asyncio
import discord
from discord.ext.commands import Context

# assumes page content was already sorted out beforehand
async def run_paged_message(ctx: Context, embed_pages):
    message = await ctx.send(embed=embed_pages[0])
    
    double_left_arrow = '⏪'
    double_right_arrow = '⏩'
    left_arrow = '◀'
    right_arrow = '▶'
    delete = '❎'
    emojis = [double_left_arrow, left_arrow, right_arrow, double_right_arrow, delete]
    
    index = 0
    
    for e in emojis:
        await message.add_reaction(e)

    def check(react, user):
        return user == ctx.author and react.emoji in emojis and react.message.id == message.id

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=600, check=check)
            if reaction.emoji == delete:
                await message.delete()
                return
            
            new_index = index
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
                await message.remove_reaction(emoji, ctx.bot.user)
            break