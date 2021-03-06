# bot.py
# main MiikoBot class

from queue import Queue
from discord.ext import commands
from tortoise import Tortoise

from tortoise_config import TORTOISE_ORM

class MiikoBot(commands.Bot):
    player = {} # might move to models to better manage large queues, keep from clogging mem
    playing = {}

    def __init__(self, *args, **kwargs):
        self.extension_names = set()
        super().__init__(*args, **kwargs)

    def load_extension(self, name):
        self.extension_names.add(name)
        super(MiikoBot, self).load_extension(name)

    def unload_extension(self, name):
        self.extension_names.remove(name)
        super(MiikoBot, self).unload_extension(name)

    def reload_all_extensions(self):
        for ext in self.extension_names:
            self.reload_extension(ext)

    # override bot login to init tortoise orm connection on start
    async def login(self, token, *, bot=True):
        await Tortoise.init(TORTOISE_ORM)
        await super(MiikoBot, self).login(token, bot=bot)