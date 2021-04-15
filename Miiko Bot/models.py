# models.py
# tortoise orm models 

from discord.ext import commands
from tortoise import Model, fields
from tortoise.models import ModelMeta
from enum import Enum

# model for event db
class D4DJEvent(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(255)
    embedname = fields.CharField(255, default=None, null=True) # shortened name for embed list
    artist = fields.CharField(6) # include number corresponding to each artist (see artist array in aliases.py)
    eventdate = fields.CharField(19) # expected in "[YYYY]-[MM]-[DD]T[hh]:[mm]:[ss]" form

    # livestream and archive expected in the form "[text](link)" for links
    livestream = fields.TextField(default=None, null=True)
    archive = fields.TextField(default=None, null=True)
    logo = fields.TextField(default=None, null=True)
    guests = fields.TextField(default=None, null=True) # using this only for main D4DJ events, if part of a split/guesting will leave blank

    class Meta:
        table = "Events"

# model for song management
class D4DJSong(Model):
    id = fields.IntField(pk=True) # id determined by group id + song num (i.e. 405 would be RONDO's 5th song)
    name = fields.CharField(255)
    jpname = fields.CharField(255)
    romanizedname = fields.CharField(255) # might replace with pykakasi conversion
    artist = fields.CharField(7) # same as event artist but 7th char [9] to indicate special artist. will override artist embed output with custom string
    artiststr = fields.CharField(255, defualt=None, null=True)
    length = fields.IntField() # time in seconds
    original = fields.BooleanField(default=True)

# model for guild/channel pref management. 
# will likely need base class for guild/channel, just doing this for now so i can learn to use the orm...
class Guild(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField(max_length=255)

    class Meta:
        table = "Guilds/Servers"

    @classmethod
    async def get_from_context(cls, ctx):
        if not ctx.guild:
            return None
        return (await cls.update_or_create(id=ctx.guild.id, name=ctx.guild.name))[0]

    def __str__(self):
        return f'{self.name} ({self.id})'