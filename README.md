# discordbot
A Discord bot I put together to make life easier for server moderation.


## Dependencies / acknowledgements
* Python 3.5 or above
* [discord.py](https://github.com/Rapptz/discord.py)



## Main features
* Enable general members to add or remove particular roles on themselves.
* Dice, coin toss, 8 ball and choose from list commands
* Purge messages from a channel or messages by a particular user
* Scans for new users it missed while being offline and logs who has been approved in its absence to bring records up to date.
* Poll system so moderators can take a vote on a question from all server members
* Create shared notes and logged warnings that other mods can see, stored against the users profile in the bot db.
* DMs a member when a new warning is logged
* Greeting system for new users with optional "gated community" settings
* Watch list to re-post what certain users said.
* Announcement command so moderators can post an announcement as "the server" rather than themselves.
* Ranking/level system
* Quote system for replying to older posts
* Anti-spam system
* Credit/play currency system
* Member profiles with customizable fields and profile search functions
* Plugin based system
* Customizable permissions
* Detect which invite a new member used to join, and which existing member invited them using the invite plugin
* Quick "timeout" system to temporarily deny a member access to all channels apart from those specified
* Tracks channel post-count statistics
* Tracks member post-count statistics, frequented channels and the days and times they are active on average.


## Upcoming features
* Public games and private games for 1v1 play in DM
* Music system
* Channel polls for general members


## Installation and first time set up

This section assumes you've already downloaded the bot files and extracted them somewhere.

### 1) Install discord.py

First you should make sure you have discord.py installed, which you can do by running the command:
```python3 -m pip install -U discord.py[voice]```


### 2) Get a Discord Bot Token

**2.1)** Get a bot token from the [Discord Applications website](https://discordapp.com/developers/applications/me)

**2.2)** Assign a bot account to it

**2.3)** Authorise that bot to join your guild by being signed into the Discord web client. Then going to this utterly ridiculous link the Discord folks couldn't be bothered to put behind a button in the App control panel, for reasons unknown to science:

https://discordapp.com/api/oauth2/authorize?client_id=YOUR_BOTS_CLIENT_ID_GOES_HERE&scope=bot&permissions=0

**2.4)** Open config.conf and paste your bot token in place of the default entry "bot-token-goes-here", save the changes and close that file.

### 3) Start the bot

**3.1)** Start the bot via a terminal command, such as:
```python3.5 /path/to/bot.py```

**3.2)** The first time the bot starts up, it will create its database (bot.db), and it will also create encryption keys. Three files will be generated "master_pass", "salt" and "pass_verif". Once the bot has started up you should copy the master_pass and salt files somewhere safe and delete them from the bots working directory, but keep the pass_verif file where it is.

The master_pass and salt files MUST be present when the bot starts up otherwise it will just error and stop.

**3.3)** Now that the bot is connected to your server, you must ensure that it has all appropriate permissions and roles are assigned to it so it can read and send messages.

**After this all commands listed are typed into the Discord client itself and not the terminal.**


### 4) Setup bot basics (required)

**4.1)** By default the bot will DM the server owner with its logs, to set a default channel the bot should post its logs to instead, run:

```/set log_channel CHANNEL-NAME```

Do not put a hash (#) in front of the channel name you are entering.

**4.2)** Permission groups are used to decide which commands or plugins any given member is allowed to use. By default there are three permission groups "owner", "admins" and "members". You can also create additional custom permission groups. Permission groups can have any number of roles or specific users attached to them, to define who falls into what group, if any.

First you're going to want to set the name of the role which you give to moderators/admins on your server by adding that role to your admins permission group:

```/permission add_role admins MOD-ROLE-NAME```

Instead of specifying a role name you can also use either "server_owner" or "server_everyone" should it be required.

By default the members permission group has the role "server_everyone" applied. If however your server has a special role which all approved members have, you may want to remove everyone from the members group and then you'll need to add your members role in its place by running:

```/permission del_role members server_everyone```
then:
```/permission add_role members MEMBER-ROLE-NAME```

This will only allow your approved members to run member level commands.

If you want to create some custom permission groups or go above and beyond this configuration, you can find the commands to do so by running ```/help bot```.


### 5) Activating plugins and setting permissions

**5.1)** By default all the plugins are disabled, you can see a list of the available plugins and their status by running:

```/plugin list```

To activate a plugin, run:

```/plugin activate PLUGIN-TAG```
For example if we were activating the server guard plugin, we would run
```/plugin activate guard```

Deactivating a plugin works the same way:
```/plugin deactivate PLUGIN-TAG```

**5.2)** Once you've activated a plugin, you may want to review its permissions to see which groups can do what with it. To see a plugins permission settings, run:

```/permission list PLUGIN-TAG```

If you want to add or remove permission groups from a particular plugin, you can run either:

```/permission allow_group PERMISSION-SET GROUP-NAME```
or
```/permission revoke_group PERMISSION-SET GROUP-NAME```

PERMISSION-SET is typically the plugin tag and the permission in question separated by a colon. For example if the plugin where "stats" and the permission in question were "view_stats" then the PERMISSION-SET would be "stats:view_stats"


### 6) Continue setting up

As you activate more plugins and review their permissions, you will also want to check the help menu for those plugins as some have additional settings and channels that can be used.

You can see the main help menu contents by running

```/help```

and you can see the help menu for a particular plugin by running

```/help PLUGIN-TAG```


## \o/ Thats it, enjoy! Or don't! I couldn't care less :D

You can see the full list of commands available and how to use them by running:

```/help```

Please note that you must be the server owner, or have the moderators role attached to you, in order for the help menu to display moderator level commands. General users get a much shorter list of command options.
