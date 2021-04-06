# Miiko Bot
A novelty Discord bot created for the purpose of learning to code Discord bots.

## Setup

### .env file
A .env file should be created in the Miiko Bot directory. It should have the following values:
 - DISCORD_TOKEN set to the bot token
 - BOT_OWNER set to the user ID of the owner of the bot

### DB initialization
init_db.py needs to be run before main.py to generate models/schema on postgres db.
Change TORTOISE_ORM in tortoise_config.py to your needs before running.

## Planned Features

### D4DJ Information Database
Utility feature to find requested information on D4DJ lives, music, and seiyuu

### Music Player
Allows for bot to join voice channels and play back D4DJ related music
(Currently only features 'play', ability to play a single song)