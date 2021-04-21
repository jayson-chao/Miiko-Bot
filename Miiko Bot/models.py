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
        ordering = ["id"]

# model for song management
class D4DJSong(Model):
    id = fields.IntField(pk=True) # id determined by group id (1) + orig/cover (1) + song num (3) (i.e. 40005 would be rondo's 5th original)
    name = fields.CharField(255)
    jpname = fields.CharField(255, default=None, null=True)
    romanizedname = fields.CharField(255, default=None, null=True) # might replace with pykakasi conversion
    artist = fields.CharField(7) # same as event artist but 7th char [9] to indicate special artist. will override artist embed output with custom string
    artiststr = fields.CharField(255, default=None, null=True)
    length = fields.IntField(null=True, default=None) # time in seconds
    original = fields.BooleanField(default=True)
    album = fields.ForeignKeyField('models.D4DJAlbum', related_name='songs', null=True, default=None)
    track = fields.IntField(null=True, default=None) # related to album

    # playable songs in common/assets/music (instr. tracks planned to be same id + 'i')

    class Meta:
        table = "Songs"
        ordering = ["id"]
        unique_together = (("album_id", "track"))

class D4DJAlbum(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(255)
    jpname = fields.CharField(255, default=None, null=True)
    romanizedname = fields.CharField(255, default=None, null=True) # might replace with pykakasi conversion
    artist = fields.CharField(7) # same as event artist but 7th char [9] to indicate special artist. will override artist embed output with custom string
    artiststr = fields.CharField(255, default=None, null=True)
    releasedate = fields.CharField(10) # YYYY-MM-DD format

    class Meta:
        table = "Albums"
        ordering = ["id"]

# model for guild/channel pref management. 
# will likely need base class for guild/channel, just doing this for now so i can learn to use the orm...
class Guild(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField(max_length=255)

    class Meta:
        table = "Guilds/Servers"
        ordering = ["id"]

    def __str__(self):
        return f'{self.name} ({self.id})'