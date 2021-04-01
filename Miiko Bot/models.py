# models.py
# tortoise orm models 

from discord.ext import commands
from tortoise import Model, fields
from tortoise.models import ModelMeta

# model for event db
class D4DJEvent(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    event_time = fields.DatetimeField()
    main_artist = fields.IntField() # in six digit format, 0 or 1 to rep. each performing artist. 

    class Meta:
        table = "Events"

# model for guild/channel pref management. 
# will likely need base class for guild/channel, just doing this for now so i can learn to use the orm...
class Guild(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField(max_length=255)
    response_pref = fields.BooleanField(default=True)
    react_pref = fields.BooleanField(default=False)
    msg_channel = fields.BigIntField(null=True, default=None)

    class Meta:
        table = "Guilds/Servers"

    @classmethod
    async def get_from_context(cls, ctx):
        if not ctx.guild:
            return None
        return (await cls.update_or_create(id=ctx.guild.id, name=ctx.guild.name))[0]

    def __str__(self):
        return f'{self.name} ({self.id})'