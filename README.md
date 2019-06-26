# noDoot // Member verification taken to the next level
noDoot is a Discord bot developed by HeroGamers#0001, which denies Userbots from joining your guild, effictively stopping all DM and server spam from those bots that have been quite active on Discord lately.  
noDoot is developed as a submission for Discord's Hack Week 2019, in the moderation category. Therefore I will not be taking any PR's untill the Hack Week is over.

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ca53c7dfceee43ba945f58f580fcc70f)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Fido2603/noDoot&amp;utm_campaign=Badge_Grade)

___

[![noDoot Banner](https://raw.githubusercontent.com/Fido2603/noDoot/master/img/nodoot-readme.png)](https://discordapp.com/oauth2/authorize?client_id=592829567660457985&scope=bot&permissions=2)
## How noDoot keeps the UserDoots away
noDoot works by taking users who are joining a server, sending them an invite to the noDoot Verification Server, and kicking them after five minutes, if they aren't verified yet.  
On the noDoot Verification Server, the user is sent a Captcha through their DM's, and once verified, the user will be able to join all servers using noDoot, and should never need to do the verification again, ever, because don't we all hate doing Captcha's?

## How to get rid of UserDoots from your server
**WARNING BEFORE ADDING THE BOT:** ***Adding this bot to your server definitely helps with keeping the userbots away for your server, but for smaller servers it may also cause less members to actually join the server, as they would see it as a hassle to complete the verification process!***

You can invite noDoot to your servers, and thus enable the verification process on them, using these invite links:

[![Invite noDoot - Kick Members](https://img.shields.io/static/v1.svg?label=Invite%20noDoot&message=Kick%20Permission&color=7289DA&stile=flat&logo=discord&logoColor=7289DA&labelColor=2C2F33)](https://discordapp.com/oauth2/authorize?client_id=592829567660457985&scope=bot&permissions=2)  
[![Invite noDoot - Invite Members](https://img.shields.io/static/v1.svg?label=Invite%20noDoot&message=Invite%20Permission&color=7289DA&stile=flat&logo=discord&logoColor=7289DA&labelColor=2C2F33)](https://discordapp.com/oauth2/authorize?client_id=592829567660457985&scope=bot&permissions=3)

*The Kick Members Permission is required, but can be given through other roles if wanted. The Create Instant Invite Permission is optional, but is required if you want the bot to give the user a new invite back to the server they tried to join, if kicked.*

### Leaving Feedback
I would be very happy if you could give some feedback on the bot, after you have tried the verification process. After the verification process is done, the bot will send an invite to my server, Treeland, where you can then afterwards send me a DM through.

### Running the bot locally
Running the bot locally is not recommended, but it can be done.  
1. Install Python 3.6.6
2. Run `pip install -r requirements.txt` in the bot's root directory.
   * Sometimes Pillow is having missing dependencies, on Debian-based distros, at which you need to run `sudo apt-get install libjpeg-dev zlib1g-dev` (it should be somewhat the same with apk).
3. Copy "configexample.py", and rename it to "config.py". Fill out the config file.
4. Run bot.py
