import discord, asyncio
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

        # This is the function that we run when a member tries to join a guild, but they don't have DM's enabled...
        async def memberNoDMProcedure(member, guild):
            channel_found = False # We want to have a variable that says whether we found a valid channel to remind the user in...
            # Now to go through the channels
            for channel in guild.channels:
                if channel_found == False:
                    # we don't want categorychannels and voicechannels
                    if isinstance(channel, discord.CategoryChannel) or isinstance(channel, discord.VoiceChannel):
                        continue
                    # and then we check the permissions for the user
                    user_permissions = channel.permissions_for(member)

                    # and we check if the user can read messages in that channel
                    if user_permissions.read_messages:
                        # and now we check if we, the bot, can write in that channel!
                        bot_member = guild.get_member(bot.user.id)
                        bot_permissions = channel.permissions_for(bot_member)

                        if bot_permissions.send_messages:
                            # yessir, we found a channel where we can notify the user!

                            message = await channel.send(content="Hello there " + member.mention + "! You have joined a server protected by noDoot, but it doesn't seem like you have DM's enabled, since I've tried sending you one!\n" +
                                "Please verify your account on this server: <https://discord.gg/9kQ7Mvm>, and then try joining again!\n\n**This message will self-destruct in five minutes, and you will be kicked from the server if you haven't verified yourself!**")
                            channel_found = True
                            break
            if channel_found:
                # do something
                await logger.log("A channel has been found, and a message has been sent on the server! Sleeps for five minutes, and then kicks user, if not verified...", bot, "INFO")
                await asyncio.sleep(300) # wait five minutes before kicking the user, and deleting the message

                # delete the message
                try:
                    await message.delete()
                except Exception as e:
                    await logger.log("Failed to delete the verify message in the server: " + member.guild.name, bot, "WARNING")

                if isUserVerified(member.id):
                    await logger.log("User has verified themselves, stopping kick: " + member.name + " / " + str(member.id), bot, "INFO")
                    return

                # If user hasn't verified themselves, kick the user
                try:
                    await member.kick(reason="noDoot - User needs to be verified.. couldn't send DM to user. Reminded on the server")
                except Exception as e:
                    await logger.log("Could not kick the user from the guild. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name + " - Error: " + str(e), bot, "DEBUG")
                    return
                await logger.log("Kicked a user from joining a guild, not verified. Couldn't send DM. Reminded on the server. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "DEBUG")

                return
            else:
                # no channel found, let's notify the owner of the guild...
                owner = member.guild.owner
                # We will now try to send them a DM
                dm_channel = owner.dm_channel
                if dm_channel == None:
                    await owner.create_dm()
                    dm_channel = owner.dm_channel

                # Send message
                try:
                    await dm_channel.send(content="Hello there! On your guild (" + guild.name + "), it doesn't seem like there is a channel where both new members can see messages, and where I can write messages!\n" +
                        "This means that the user: " + member.name + "`" + member.id + "`, that just tried to join your server, hasn't verified their account yet! Please setup a channel where I can write, and new users can read!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off
                    await logger.log("Couldn't send DM to owner of server. Owner ID: " + str(owner.id) + " Guild: " + guild.name + " - Error: " + str(e), bot, "WARNING")
                    return
                await logger.log("Sent the DM's to the owner sucessfully! User: " + owner.name, bot, "DEBUG")
                return

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
        await logger.log("New member tried to join somewhere! Member: " + member.name + " - Guild: " + member.guild.name, bot, "DEBUG")
        if member.guild.id == int(os.getenv('nDGuild')):
            if isUserVerified(member.id):
                await logger.log("Already verified user tried to join noDoot: " + member.name + " / " + str(member.id), bot, "DEBUG")
                await member.kick(reason="noDoot - User already verified!")
            return

        # We check if the user is already a verified user
        if isUserVerified(member.id):
            await logger.log("User is verified. Letting them join! User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "DEBUG")
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
            # if we can't send the DM, the user probably has DM's off, at which point we would send them a heads-up in the server they're trying to join, and then kick them a minute or so afterwards
            await logger.log("Couldn't send DM to user that joined. Member ID: " + str(member.id) + " - Error: " + str(e), bot, "WARNING")
            await memberNoDMProcedure(member, member.guild)
            return

        await dm_channel.send(content="**You have been kicked from a server protected from userbots by noDoot..**\nTo verify yourself across all servers using noDoot, please join this server to start the verification process: https://discord.gg/9kQ7Mvm\n\n*You are automatically kicked from the verification server after verification...*")
        await logger.log("Sent the DM's to the user sucessfully! User: " + member.name, bot, "DEBUG")
        # And then we kick them, for now.
        try:
            await member.kick(reason="noDoot - User needs to be verified..")
        except Exception as e:
            await logger.log("Could not kick the user from the guild. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name + " - Error: " + str(e), bot, "DEBUG")
            return
        await logger.log("Kicked a user from joining a guild, not verified. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "DEBUG")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
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

        # we check whether the reaction added is from the verification channel
        if payload.channel_id == int(os.getenv('verificationChannel')):
            await logger.log("A reaction has been added in the verification channel! User ID: " + str(user.id), bot, "DEBUG")
            # Checking whether the user already is verified
            if isUserVerified(userid):
                await logger.log("Already verified! User ID: " + str(user.id), bot, "DEBUG")
                return

            if user.bot == True:
                return

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
                await logger.log("Couldn't send DM to user that reacted. User ID: " + str(user.id) + " - Error: " + str(e), bot, "INFO")
                # send a headsup in the verification channel
                channel = bot.get_channel(int(os.getenv('verificationChannel')))
                await channel.send(content=user.mention + " Sorry! It seems like your DM didn't go through, we're on the case!", delete_after=float(30))
                return

            # generate a captcha
            captcha = generateCaptcha()

            # send the message
            await logger.log("Verification sent to user: " + str(user.id), bot, "DEBUG")
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
        # check if it's a DM
        if isinstance(message.channel, discord.DMChannel):
            await logger.log("New message in the DM's", bot, "DEBUG")
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

            await logger.log("User: " + message.author.name + " `" + str(message.author.id) + "` - Captcha Text: " + captcha_text + " - Message content: " + message.content, bot, "DEBUG")

            # if the message content is equals to that of the message
            if message.content == captcha_text:
                # If the user is already verified, do nothing
                if isUserVerified(message.author.id):
                    await logger.log("User tried to do captcha again, but are already verified! User: " + message.author.name, bot, "DEBUG")
                    return
                # if not, add them to the verified file
                addUserToVerified(message.author.id)
                # Send completion message
                await logger.log("User completed captcha sucessfully! Added to verified users! User: " + message.author.name + "`" + str(message.author.id) + "`", bot, "INFO")
                await message.channel.send(content="**Captcha completed successfully!**\nYour account is now verified!")
                # Kick from the noDoot Server
                await bot.get_guild(int(os.getenv('nDGuild'))).kick(message.author, reason="noDoot - User verified sucessfully!")
                return
            # if not
            await message.channel.send(content="**Incorrect answer! Try again...**\n*If the captcha won't work, contact HeroGamers#0001 on the noDoot Server!*")

def setup(bot):
    bot.add_cog(listenerCog(bot))
