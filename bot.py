import os, discord
from discord.ext import commands
from discord import File
from utilities import logger
try:
    import config
except ImportError:
    print("Couldn't import config.py")

# We load the bot
bot = commands.Bot(command_prefix=os.getenv('prefix'), description="Holding out UserDoots from guilds since the Discord Hack Week 19.\n" +
                                                                    "A Discord bot made by HeroGamers#0001, using the discord.py library.")

# And define which extensions we want to have loaded at startup
startup_extensions = ["listenerCog",
                      "administration",
                      "info"]

@bot.event
async def on_ready():
    # we setup the logger first
    logger.setup_logger()

    # change the bot presence
    await bot.change_presence(activity=discord.Game(name="around with new members... [" + os.getenv('prefix') + "help]"))

    # check for the message in the verification channel, if it's not there, send it.
    channel = bot.get_channel(int(os.getenv('verificationChannel')))
    history = await channel.history(limit=5).flatten()
    # check if no messages
    if len(history) == 0: # no messages
        # Sending the message
        await logger.log("Sending the verification message...", bot, "INFO")
        await channel.send(file=File("./img/nodoot_verify.png"))
        vmessage = await channel.send(content="Hello there! Welcome to the noDoot Verification Server! Don't worry, you won't be here for long...\n" +
            "\nFirst of all, I need you to be sure to have DM's enabled for this server.\nAfter that, please click the reaction to this message, to begin the verification process!")

        # now we add a reaction to the message
        await vmessage.add_reaction("✅")

    # Bot startup is now done...
    logger.logDebug("----------[LOGIN SUCESSFULL]----------", "INFO")
    logger.logDebug("     Username: " + bot.user.name, "INFO")
    logger.logDebug("     UserID:   " + str(bot.user.id), "INFO")
    logger.logDebug("--------------------------------------", "INFO")
    await logger.log("Bot startup done.", bot, "INFO", "Bot startup done.\n")

@bot.event
async def on_guild_join(guild):
    await logger.log("Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")

# We load the extensions
if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            logger.logDebug(f"Failed to load extension {extension}. - {e}", "ERROR")

# And run the bot
bot.run(os.getenv('token'))
