# models.py
# tortoise orm models 

from discord.ext import commands
from tortoise import Model, fields
from tortoise.models import ModelMeta

from common.aliases import LangPref

# model for event db
class D4DJEvent(Model):
    id = fields.IntField(pk=True) # id system - [0/Live, 1/DJ_TIME, 2/Other D4DJ Stream, 3/Other Event][03d - setlist number]
    name = fields.CharField(255)
    embedname = fields.CharField(255, default=None, null=True) # shortened name for embed list
    artist = fields.ManyToManyField('models.Artist', related_name='performed', through='performers')
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
    artist = fields.CharField(7, default="9") # same as event artist but 7th char [9] to indicate special artist.
    artiststr = fields.ForeignKeyField('models.Artist', related_name='song_str', null=True, default=None)
    orartist = fields.ForeignKeyField('models.Artist', related_name='or_by', null=True, default=None)
    lyricist = fields.ManyToManyField('models.D4DJStaff', related_name='lyricized', through='lyricists', null=True, default=None)
    composer = fields.ManyToManyField('models.D4DJStaff', related_name='composed', through='composers', null=True, default=None)
    arranger = fields.ManyToManyField('models.D4DJStaff', related_name='arranged', through='arrangers', null=True, default=None)
    length = fields.IntField(null=True, default=None) # time in seconds
    album = fields.ForeignKeyField('models.D4DJAlbum', related_name='songs', null=True, default=None)
    track = fields.IntField(null=True, default=None) # related to album
    # add: fks to staff

    # playable songs in common/assets/music (instr. tracks planned to be same id + 'i')
    # external songs will be numbered from 92001 onwards

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
    artiststr = fields.ForeignKeyField('models.Artist', related_name='alb_str', null=True, default=None)
    releasedate = fields.CharField(10) # YYYY-MM-DD format

    class Meta:
        table = "Albums"
        ordering = ["id"]

class D4DJSetlist(Model):
    event = fields.ForeignKeyField('models.D4DJEvent')
    song = fields.ForeignKeyField('models.D4DJSong')
    position = fields.IntField()

    class Meta:
        table = "setlist_songs"
        ordering = ["event__id", "position"]
        unique_together = (("event", "position")) 

class Artist(Model):
    name = fields.CharField(255, pk=True)
    jpname = fields.CharField(255, default=None, null=True)

    class Meta:
        table = "Artists"

class D4DJChara(Model):
    name = fields.CharField(255)
    jpname = fields.CharField(255)
    seiyuu = fields.ForeignKeyField('models.D4DJSeiyuu')
    birthday = fields.CharField(5) # MM-DD

    class Meta:
        table = "Characters"

class D4DJSeiyuu(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(255)
    jpname = fields.CharField(255)
    agency = fields.CharField(255)
    birthday = fields.CharField(10) # YYYY-MM-DD

    class Meta:
        table = "Seiyuu"

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