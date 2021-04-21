# Miiko Bot
A novelty Discord bot created for the purpose of learning to code Discord bots.

## Setup

### .env file
A .env file should be created in the Miiko Bot directory. It should have the following values:
 - DISCORD_TOKEN set to the bot token

### DB initialization
init_db.py needs to be run before main.py to generate models/schema (I'm using Postgres).  
Change TORTOISE_ORM in tortoise_config.py to your needs before running.

## Current Features

### D4DJ Information Database
- Event info commands which feature event information embeds that show info including  
  timing to upcoming events and links to streams/archives
- [60% Done] Music info commands including basic song information and album track listings,  
  now with server-scoped preference settings to show names in EN/JP/Romanized

### Music Player
- [90% Done] Allows for Miiko Bot to join voice channels and play released D4DJ songs.  
  Features play/pause and song queueing functions. (Limited to 7 songs at the moment)

## Planned Features

### D4DJ Information Database
- Expand music embeds to include production team information like arrangers/composer/lyricists.
- Add information commands for livestreams/relevant DJ sets
- Show setlists for past events/DJ sets
- Expand upon the existing archive links to allow for searching of archive content

### Music Player
- Feature "now playing" embeds and song queueing directly from song info embeds
- Allow for playback of past live events/sets with track listing and scene selection

## Contact
A running instance of Miiko can be tested over on the [Miiko Bot Discord server](https://discord.gg/HChrpwVVHU).

