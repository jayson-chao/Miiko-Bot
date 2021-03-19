# bot.py
# main MiikoBot class

from discord.ext import commands

class MiikoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.extension_names = set()
        super().__init__(*args, **kwargs)

    def load_extension(self, name):
        self.extension_names.add(name)
        super(MiikoBot, self).load_extension(name)

    def unload_extension(self, name):
        self.extension_names.remove(name)
        super(MiikoBot, self).unload_extension(name)
