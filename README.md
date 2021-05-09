# Miiko Bot
A novelty Discord bot created for the purpose of learning to code Discord bots.

## Setup

### Bot Token
Current bot implementation uses redis to fetch the bot token, remove/rewrite to your own
preferences.

### DB initialization
init_db.py needs to be run before main.py to generate models/schema on an existing database.
Change TORTOISE_ORM in tortoise_config.py to your needs before running.

## Current Features

### D4DJ Information Database
- Event info commands which feature event information embeds that show info including  
  timing to upcoming events and links to streams/archives
- Music info commands including basic song information and album track listings,  
  now with server-scoped preference settings to show names in EN/JP/Romanized
- [In Progress] Staff member-related commands. Currently has ability to list songs that
  each staff member worked on
- [In Progress] Setlist commands that show event/stream setlists. Currently has a limited
  selection of setlists available to view
- [In Progress] Stream/DJTIME info commands that have the same functions as event commands.
  Currently has one DJTIME in the database, more coming soon.

### Music Player
- Allows for Miiko Bot to join voice channels and play released D4DJ songs.  
  Features play/pause and song queueing functions. (Song selection is limited at the moment)

## Planned/Possible Features

### D4DJ Information Database
- Expand upon the existing archive links to allow for searching of archive content
- Some commands related to seiyuu information (i.e. birthday tracking)

### Music Player
- Allow for playback of past live events/sets with track listing and scene selection

## Contact
A running instance of Miiko can be tested over on the [Miiko Bot Discord server](https://discord.gg/HChrpwVVHU).

You can also invite Miiko using [this invite link](https://discord.com/api/oauth2/authorize?client_id=822237835947409458&permissions=37088576&scope=bot). Please keep in mind that Miiko is active 
development so functionalities are incomplete/may change.