import asyncio
import discord
from discord import File
from discord.ext import commands
from utilities import logger
from captcha.image import ImageCaptcha
import os, random, string

class listenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        bot = self.bot

        def isUserVerified(userID):
            # We check the verifiedUsers file...
            try:
                with open("verifiedUsers.txt", "r") as file:
                    ids = [line.rstrip('\n') for line in file]
            except IOError:
                with open("verifiedUsers.txt", "w") as file:
                    ids = [line.rstrip('\n') for line in file]

            # and check if the user id is in the file
            if str(userID) in ids:
                return True
            else:
                return False

        # We check if the member is a bot
        if member.bot == True:
            return

        # if the member joined the main guild, do nothing
        await logger.log("New member joined somewhere! Member: " + member.name + ". Guild: " + member.guild.name, bot, "DEBUG")
        if member.guild.id == int(os.getenv('nDGuild')):
            if isUserVerified(member.id):
                await member.kick(reason="noDoot - User already verified!")
            return

        # We check if the user is already a verified user
        if isUserVerified(member.id):
            return

        # We will now try to send them a DM, with the verification server linked (as they can't DM the bot without sharing any servers with it)
        dm_channel = member.dm_channel
        if dm_channel == None:
            await member.create_dm()
            dm_channel = member.dm_channel

        # Send first image
        try:
            await dm_channel.send(file=File("./img/hellothere.png"))
        except Exception as e:
            # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back to this later
            await logger.log("Couldn't send DM to user that joined. Member ID: " + member.id + ". Error: " + e, bot, "WARNING")
            await member.kick(reason="noDoot - User needs to be verified.. couldn't send DM to user")
            return

        await dm_channel.send(content="**You have been kicked from a server protected from userbots by noDoot..**\nTo verify yourself across all servers using noDoot, please join this server to start the verification process: https://discord.gg/9kQ7Mvm\n\n*You are automatically kicked from the verification server after verification...*")

        # And then we kick them, for now.
        await member.kick(reason="noDoot - User needs to be verified..")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        logger.logDebug("A reaction has been added!", "DEBUG")
        bot = self.bot
        userid = payload.user_id
        channel = bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(userid)

        def isUserVerified(userID):
            # We check the verifiedUsers file...
            try:
                with open("verifiedUsers.txt", "r") as file:
                    ids = [line.rstrip('\n') for line in file]
            except IOError:
                with open("verifiedUsers.txt", "w") as file:
                    ids = [line.rstrip('\n') for line in file]

            # and check if the user id is in the file
            if str(userID) in ids:
                return True
            else:
                return False

        def generateCaptcha():
            # First we generate a random string to use
            chars = string.ascii_letters + string.digits
            text = ''.join(random.choice(chars) for x in range(5))

            # And generate the captcha
            captchaimage = ImageCaptcha()

            image = captchaimage.generate_image(text)

            # Now to add some noise
            captchaimage.create_noise_curve(image, image.getcolors())
            captchaimage.create_noise_dots(image, image.getcolors())

            # Now to write the file
            imagefile = "./img/captcha_" + text + ".png"
            captchaimage.write(text, imagefile)

            return imagefile

        if isUserVerified(userid):
            logger.logDebug("Already verified!", "DEBUG")
            return

        # we check whether the reaction added is from the verification channel
        if payload.channel_id == int(os.getenv('verificationChannel')):
            # if yes, send the user the verification message...
            dm_channel = user.dm_channel
            if dm_channel == None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send first image
            try:
                await dm_channel.send(file=File("./img/verification.png"))
            except Exception as e:
                # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back to this later
                await logger.log("Couldn't send DM to user that reacted. User ID: " + user.id + ". Error: " + e, bot, "INFO")
                # send a headsup in the verification channel
                channel = bot.get_channel(int(os.getenv('verificationChannel')))
                await channel.send(content=user.mention + " Sorry! It seems like your DM didn't go through, we're on the case!", delete_after=float(30))
                return

            # generate a captcha
            captcha = generateCaptcha()

            # send the message
            await dm_channel.send(content="Now, to finish your verification process and gain access to servers using noDoot, please complete the captcha below!\n\n*If the captcha is not working, remove and add the reaction again, to create a new captcha, or contact HeroGamers#0001 in the noDoot Verification Server!*", file=File(captcha))

            # Delete the captcha from the filesystem
            os.remove(captcha)

    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot

        def addUserToVerified(userID):
                with open("verifiedUsers.txt", "a") as file:
                    file.write(str(userID) + "\n")

        def isUserVerified(userID):
            # We check the verifiedUsers file...
            try:
                with open("verifiedUsers.txt", "r") as file:
                    ids = [line.rstrip('\n') for line in file]
            except IOError:
                with open("verifiedUsers.txt", "w") as file:
                    ids = [line.rstrip('\n') for line in file]

            # and check if the user id is in the file
            if str(userID) in ids:
                return True
            else:
                return False

        # return if author is a bot (we're also a bot)
        if message.author.bot:
            return
        logger.logDebug("New message!", "DEBUG")
        # check if it's a DM
        if isinstance(message.channel, discord.DMChannel):
            logger.logDebug("And it's in the DM's", "DEBUG")
            # check if we even sent any captcha
            captcha_text = ""
            notFound = True
            async for oldmessage in message.channel.history(limit=150):
                if (oldmessage.author == bot.user) and notFound:
                    if len(oldmessage.attachments) != 0:
                        for attachment in oldmessage.attachments:
                            filename = attachment.filename
                            if "captcha_" in filename:
                                captcha_text = filename.replace("captcha_", "").replace(".png", "")
                                notFound = False
            if notFound:
                return

            logger.logDebug("Captcha Text: " + captcha_text + ". Message content: " + message.content)

            # if the message content is equals to that of the message
            if message.content == captcha_text:
                # If the user is already verified, do nothing
                if isUserVerified(message.author.id):
                    logger.logDebug("Already verified!", "DEBUG")
                    return
                # if not, add them to the verified file
                addUserToVerified(message.author.id)
                # Send completion message
                await message.channel.send(content="**Captcha completed successfully!**\nYour account is now verified!")
                # Kick from the noDoot Server
                await bot.get_guild(int(os.getenv('nDGuild'))).kick(message.author, reason="noDoot - User verified sucessfully!")
                return
            # if not
            await message.channel.send(content="**Incorrect answer! Try again...**\n*If the captcha won't work, contact HeroGamers#0001 on the noDoot Server!*")

def setup(bot):
    bot.add_cog(listenerCog(bot))
