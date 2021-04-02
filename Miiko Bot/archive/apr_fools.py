# apr_fools.py
# code used in the bot's april fools updates



# extra fields for Guild in models.py
    response_pref = fields.BooleanField(default=True)
    react_pref = fields.BooleanField(default=False)
    msg_channel = fields.BigIntField(null=True, default=None)



# chunk of code used in on_message in main, used to process messages and react/response appropriately
    if message.content == 'go to sleep, miiko': # a little easter egg command
                await message.channel.send('goodbye, nano!')
                await bot.logout()
    guild = await models.Guild.get_or_none(id=message.guild.id)
    if guild and guild.response_pref:        
        # some reactions to responses
        if (re.search('ssh|ssh|quiet|shut up', message.content.lower())) and message.content[0] != CMD_PREFIX: 
            await message.channel.send(str(bot.get_emoji(822256196575559720)))
        elif re.search('nano', message.content.lower()) and message.content[0] != CMD_PREFIX: 
            if guild.react_pref:
                await message.add_reaction('🇳')
                await message.add_reaction('🇦')
                await message.add_reaction(str(bot.get_emoji(826923642264092682)))
                await message.add_reaction('🇴')
                await message.add_reaction('‼️')
            else:
                await message.channel.send('nano!')
    # emote reacts to character names, always on
    if re.search('miiko', message.content.lower()) and message.content[0] != CMD_PREFIX: 
        eid = random.choice(list(miiko_emoji.values()))
        await message.add_reaction(str(bot.get_emoji(eid)))
    elif re.search('haruna', message.content.lower()) and message.content[0] != CMD_PREFIX: 
        await message.add_reaction(str(bot.get_emoji(768398466753757214)))
        await message.add_reaction(str(bot.get_emoji(768398467005153322)))



# setresponse command used in preference cog (preference.py)
    @commands.command(name='setresponse', help='set whether or not miiko responds to certain phrases')
    @commands.has_permissions(manage_guild=True)
    async def set_response(self, ctx, value):
        if is_bool_string(value):
            await models.Guild.update_or_create(id=ctx.guild.id, defaults={'response_pref':string_to_bool(value)})
            await ctx.send('Set message response preference, nano!')
        else:
            await ctx.send('Invalid preference setting, nano!')



# setreact command used in preference cog (preference.py)
    @commands.command(name='setreact', help='set whether miiko reacts to \'nano\' (overrides responding, requires response value to be true)')
    @commands.has_permissions(manage_guild=True)
    async def set_react(self, ctx, value):
        if is_bool_string(value):
            await models.Guild.update_or_create(id=ctx.guild.id, defaults={'react_pref':string_to_bool(value)})
            await ctx.send('Set message react preference, nano!')
        else:
            await ctx.send('Invalid preference setting, nano!')



# setchannel command in the utility cog (utility.py), set channel for bot to send send command messages to
    @commands.command(name='setchannel', help='set channel to send bot messages to')
    @commands.has_permissions(manage_guild=True)
    async def set_channel(self, ctx, channel_id):
        if channel_id.isdigit():
            await models.Guild.update_or_create(id=ctx.guild.id, defaults={'msg_channel':int(channel_id)})
            await ctx.send('Set message channel preference, nano!')
        else:
            await ctx.send('Invalid channel setting, nano!')



# send command in the utility cog (utility.py), send a user-defined string to the channel specified in preferences
    @commands.command(name='send', help='send message as bot in set channel')
    @commands.has_permissions(manage_guild=True)
    async def send_message(self, ctx, message):
        guild = await models.Guild.get_or_none(id=ctx.guild.id)
        if guild:
            channel = self.bot.get_channel(guild.msg_channel)
            # make sure bot is sending to a channel within the server - don't want cross-server posting
            if channel and channel in ctx.guild.channels: 
                await channel.send(message)
            else:
                await ctx.send('Invalid channel set, nano!')