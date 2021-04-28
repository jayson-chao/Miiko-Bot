# models.py
# tortoise orm models 

from discord.ext import commands
from tortoise import Model, fields
from tortoise.models import ModelMeta

from common.aliases import LangPref

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
    guests = fields.TextField(default=None, null=True) # using this only for main D4DJ events, if part of a split/guesting will leave blank

    class Meta:
        table = "Events"
        ordering = ["id"]

# model for song management
class D4DJSong(Model):
    id = fields.IntField(pk=True) # id determined by group id (1) + orig/cover (1) + song num (3) (i.e. 40005 would be rondo's 5th original)
    name = fields.CharField(255)
    jpname = fields.CharField(255, default=None, null=True)
    roname = fields.CharField(255, default=None, null=True) 
    artist = fields.CharField(7) # same as event artist but 7th char [9] to indicate special artist.
    artiststr = fields.ForeignKeyField('models.OtherArtist', related_name='song_str', null=True, default=None)
    orartist = fields.ForeignKeyField('models.OtherArtist', related_name='or_by', null=True, default=None)
    lyricist = fields.ManyToManyField('models.D4DJStaff', related_name='lyricized', through='lyricists', null=True, default=None)
    composer = fields.ManyToManyField('models.D4DJStaff', related_name='composed', through='composers', null=True, default=None)
    arranger = fields.ManyToManyField('models.D4DJStaff', related_name='arranged', through='arrangers', null=True, default=None)
    length = fields.IntField(null=True, default=None) # time in seconds
    album = fields.ForeignKeyField('models.D4DJAlbum', related_name='songs', null=True, default=None)
    track = fields.IntField(null=True, default=None) # related to album
    # add: fks to staff

    # playable songs in common/assets/music (instr. tracks planned to be same id + 'i')

    class Meta:
        table = "Songs"
        ordering = ["id"]
        unique_together = (("album_id", "track"))

class D4DJAlbum(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(255)
    jpname = fields.CharField(255, default=None, null=True)
    roname = fields.CharField(255, default=None, null=True) # might replace with pykakasi conversion
    artist = fields.CharField(7) 
    artiststr = fields.ForeignKeyField('models.OtherArtist', related_name='alb_str', null=True, default=None)
    releasedate = fields.CharField(10) # YYYY-MM-DD format

    class Meta:
        table = "Albums"
        ordering = ["id"]

class OtherArtist(Model):
    name = fields.CharField(255, pk=True)
    jpname = fields.CharField(255, default=None, null=True)

    # here for tl purposes but given the large amount of null fields, may just use JP name for "original artist" without TL'ing

    class Meta:
        table = "Misc. Artists"

class D4DJStaff(Model):
    name = fields.CharField(255, pk=True)
    jpname = fields.CharField(255, default=None, null=True)
    company = fields.CharField(255, default=None, null=True)
    composed: fields.ManyToManyRelation[D4DJSong]
    lyricized: fields.ManyToManyRelation[D4DJSong]
    arranged: fields.ManyToManyRelation[D4DJSong]
    
    class Meta:
        table = "Staff Members"

# model for guild + pref management. 
class Guild(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField(max_length=255)
    langpref = fields.IntEnumField(LangPref, default=LangPref.JP)

    class Meta:
        table = "Guilds/Servers"
        ordering = ["id"]

    def __str__(self):
        return f'{self.name} ({self.id})'