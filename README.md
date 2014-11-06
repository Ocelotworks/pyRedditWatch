pyRedditWatcher
============

Introduction
------------
pyRedditWatcher is an IRC bot that checks specified subreddits for new posts and announces them in the IRC channels.

Installation
------------

Install the reqired dependencies and clone the git repo:

    $ pip install unidecode
    $ sudo apt-get install python2.7
    $ git clone https://github.com/teknogeek/pyRedditWatch

Usage
-----
    
    $ python reddit.py
    
Commands
--------

*   `!add [subreddit] (color)` - add a subreddit to be checked
    *   `subreddit` - the subreddit name after /r/
        * e.g. [https://reddit.com/r/**technology**](https://reddit.com/r/technology)
    *   `(optional) color` - the color for the post announcement. You can get a list of colors using `!listcolors`
    *   Example 1: `!add technology`
    *   Example 2: `!add technology red`
*   `!del [subreddit]`
    *   `subreddit` - name of subreddit already being checked
*   `!color [subreddit] [color]`
    *   `subreddit` - the name of the subreddit already being checked
    *   `color` - new color for the post announcement. If no color is specified, a random color is chosen
*   `!list` - list the subreddits that are currently being checked
*   `!listcolors` - list available colors
   
Configuration
-------------
Copy the example configuration for the bot to read:

    $ cp settings.conf.example settings.conf
    
####Config Options####


*   `server` - IRC server address
*   `port` - IRC server port
*   `ssl` - Whether the bot should connect with SSL.
    *   True or False - **CASE SENSITIVE**
*   `isZNC` - Whether the bot is connecting to a ZNC/Bouncer
    *   True or False - **CASE SENSITIVE**
*   `nickname` - Nickname for the bot to use on IRC
*   `username` - Username for the bot to use on IRC
*   `realName` - Real Name for the bot to use on IRC
*   `identPass` - NickServ identify password
*   `zncPass` - Password for the bot to use when authenticating with the ZNC/Bouncer
*   `channels` - IRC channels for the bot to join automatically separated by ", "
