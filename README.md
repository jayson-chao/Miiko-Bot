# Miiko Bot
A novelty Discord bot created for the purpose of learning to code Discord bots.

## Setup

### Bot Token
Current bot implementation uses redis to fetch the bot token, remove/rewrite to your own
preferences.

### DB initialization
init_db.py needs to be run before main.py to generate models/schema on an existing database.
Change TORTOISE_ORM in tortoise_config.py to your needs before running.

### Assets
Some bot functions like embed images and playback files are stored in [this repo](https://github.com/jayson-chao/Miiko-Assets)

## Current Features

### D4DJ Information Database
- Event info commands which feature event information embeds that show info including  
  timing to upcoming events and links to streams/archives
- Music info commands including basic song information and album track listings
- [In Progress] Staff member-related commands. Currently has ability to list songs that
  each staff member worked on
- Setlist commands that show event/stream setlists.
- [In Progress] Stream/DJTIME info commands that have the same functions as event commands.
  Currently DJTIME streams implemented, misc. D4DJ streams and other related DJ streams coming
  soon
- Server-scoped preference setting to display song/artist/album/staff names in EN/JP/Romanized

### Music Player
- Allows for Miiko Bot to join voice channels and play released D4DJ songs.  
  Features play/pause and song queueing functions. (Song selection is limited at the moment)

## Planned/Possible Features

### Bot Settings
- Full EN/JP l10n preferences, possible CN/TW setting as well.

### D4DJ Information Database
- Expand upon the existing archive links to allow for searching of archive content
- Some commands related to seiyuu information (i.e. birthday tracking)

### Music Player
- Allow for playback of past live events/sets with track listing and scene selection

## Contact
A running instance of Miiko can be tested over on the [Miiko Bot Discord server](https://discord.gg/HChrpwVVHU).

You can also invite Miiko using [this invite link](https://discord.com/api/oauth2/authorize?client_id=822237835947409458&permissions=37088576&scope=bot). Please keep in mind that Miiko is active 
development so functionalities are incomplete/may change.