import discord, asyncio, User
from discord import File
from discord.ext import commands
from utilities import logger, captchaHandler
import os

class listenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        bot = self.bot

        # This is the function we run to try and find a channel with Create Instant Invite permissions, and where the user should be able to see the channels
        # Really similar to already-made code below (memberNoDMProcedure(member, guild)), so for comments, please view that function...
        async def memberFindInviteChannel(member, guild):
            # Adding the member to the db
            await User.add_user(member.id, member.name + "#" + member.discriminator, bot)

            # finding the invite channel
            channel_found = False
            for channel in guild.channels:
                if channel_found == False:
                    if isinstance(channel, discord.CategoryChannel) or isinstance(channel, discord.VoiceChannel):
                        continue
                    user_permissions = channel.permissions_for(member)
                    if user_permissions.read_messages:
                        bot_permissions = channel.permissions_for(guild.get_member(bot.user.id))
                        if bot_permissions.create_instant_invite:
                            # And then we log the channel-ID to the database...
                            User.add_invite(member.id, channel.id)
                            channel_found = True
                            break

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
                                "Please verify your account on this server: <https://discord.gg/9kQ7Mvm>, and then try joining again!\n\n" +
                                "**This message will self-destruct in five minutes, and you will be kicked from the server if you haven't verified yourself!**")
                            channel_found = True
                            await logger.log("Channel where message has been sent: #" + channel.name + " (`" + str(channel.id) + "`)", bot, "DEBUG")
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

                if User.isUserVerified(member.id):
                    await logger.log("User has verified themselves, stopping kick: " + member.name + " / " + str(member.id), bot, "INFO")
                    return

                # Find a channel for the user to get an invite back to
                await memberFindInviteChannel(member, guild)

                # If user hasn't verified themselves, kick the user
                try:
                    await member.kick(reason="noDoot - User needs to be verified.. couldn't send DM to user. Reminded on the server")
                except Exception as e:
                    await logger.log("Could not kick the user from the guild. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name + " - Error: " + str(e), bot, "ERROR")
                    return
                await logger.log("Kicked a user from joining a guild, not verified. Couldn't send DM. Reminded on the server. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "INFO")

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
                        "This means that the user: " + member.name + " `" + str(member.id) + "`, that just tried to join your server, hasn't verified their account yet! Please setup a channel where I can write, and new users can read!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off
                    await logger.log("Couldn't send DM to owner of server. Owner ID: " + str(owner.id) + " Guild: " + guild.name + " - Error: " + str(e), bot, "WARNING")
                    return
                await logger.log("No channel for user found, sent the DM's to the owner sucessfully! User: " + owner.name, bot, "INFO")
                return

        # We check if the member is a bot
        if member.bot == True:
            return

        # if the member joined the main guild, do nothing
        await logger.log("New member tried to join somewhere! Member: " + member.name + " - Guild: " + member.guild.name, bot, "INFO")
        if member.guild.id == int(os.getenv('guild')):
            if User.isUserVerified(member.id):
                await logger.log("Already verified user tried to join noDoot: " + member.name + " / " + str(member.id), bot, "DEBUG")
                await member.kick(reason="noDoot - User already verified!")
            return

        # We check if the user is already a verified user
        if User.isUserVerified(member.id):
            await logger.log("User is verified. Letting them join! User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "INFO")
            return

        # We will now try to send them a DM, with the verification server linked (as they can't DM the bot without sharing any servers with it)
        dm_channel = member.dm_channel
        if dm_channel == None:
            await member.create_dm()
            dm_channel = member.dm_channel

        # Send first image
        try:
            await dm_channel.send(file=File("./img/nodoot_hello.png"))
        except Exception as e:
            # if we can't send the DM, the user probably has DM's off, at which point we would send them a heads-up in the server they're trying to join, and then kick them a minute or so afterwards
            await logger.log("Couldn't send DM to user that joined. Member ID: " + str(member.id) + " - Error: " + str(e), bot, "INFO")
            await memberNoDMProcedure(member, member.guild)
            return

        await dm_channel.send(content="**You are about to be kicked from a server protected from userbots by noDoot..**\n" +
            "To verify yourself across all servers using noDoot, please join this server to start the verification process: <https://discord.gg/9kQ7Mvm>.\n" +
            "If you complete the verification within five minutes, you won't be kicked from the server that you are trying to join!\n\n" +
            "*You are automatically kicked from the verification server upon verification...*")
        await logger.log("Sent the DM's to the user sucessfully! Sleeping for five minutes, then kick if not verified. User: " + member.name, bot, "INFO")

        # sleeps for five minutes
        await asyncio.sleep(300) # wait five minutes before kicking the user, and deleting the message

        # Then we check again to see if the user has become a verified user
        if User.isUserVerified(member.id):
            await logger.log("User is verified. Stopping the kick! User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "INFO")
            return

        # Find a channel for the user to get an invite back to
        await memberFindInviteChannel(member, member.guild)

        # Not verified, kicking
        try:
            await member.kick(reason="noDoot - User needs to be verified..")
        except Exception as e:
            await logger.log("Could not kick the user from the guild. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name + " - Error: " + str(e), bot, "ERROR")
            return
        await logger.log("Kicked a user from joining a guild, not verified. User: " + member.name + " `" + str(member.id) + "` - Guild: " + member.guild.name, bot, "INFO")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        userid = payload.user_id
        channel = bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(userid)

        # we check whether the reaction added is from the verification channel
        if payload.channel_id == int(os.getenv('verificationChannel')):
            await logger.log("A reaction has been added in the verification channel! User ID: " + str(user.id), bot, "DEBUG")

            if user.bot == True:
                return

            # Checking whether the user already is verified
            if User.isUserVerified(userid):
                await logger.log("Already verified! User ID: " + str(user.id), bot, "DEBUG")
                return

            # Add the user to the db
            await User.add_user(user.id, user.name + "#" + user.discriminator, bot)

            # if yes, send the user the verification message...
            dm_channel = user.dm_channel
            if dm_channel == None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send first image
            try:
                await dm_channel.send(file=File("./img/nodoot_final_step.png"))
            except Exception as e:
                # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back to this later
                await logger.log("Couldn't send DM to user that reacted. User ID: " + str(user.id) + " - Error: " + str(e), bot, "INFO")
                # send a headsup in the verification channel
                channel = bot.get_channel(int(os.getenv('verificationChannel')))
                await channel.send(content=user.mention + " Sorry! It seems like your DM didn't go through, try to enable your DM's for this server!", delete_after=float(30))
                return

            # generate a captcha
            captcha = captchaHandler.generateCaptcha()

            # Put the captcha into the db
            User.add_captcha(user.id, captcha[1])
            await logger.log("Added captcha for user: " + user.name + " (" + str(user.id) + ") to the db. Captcha_text: " + captcha[1], bot, "INFO")

            # send the message
            appinfo = await bot.application_info()
            await logger.log("Verification sent to user: " + str(user.id), bot, "DEBUG")
            await dm_channel.send(content="Now, to finish your verification process and gain access to servers using noDoot, please complete the captcha below (the captcha may consist of **lowercase letters** and **numbers**)!\n\n" +
                "*If the captcha is not working, write `" + os.getenv('prefix') + "newcaptcha` again to generate a new captcha, or if you are stuck, then contact " + appinfo.owner.mention + " in the noDoot Verification Server through DM's!*", file=File(captcha[0]))
            # Delete the captcha from the filesystem
            os.remove(captcha[0])

    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot

        # return if author is a bot (we're also a bot)
        if message.author.bot:
            return

        # check if it's a DM
        if isinstance(message.channel, discord.DMChannel):
            await logger.log("New message in the DM's", bot, "DEBUG")

            if not User.isUserVerified(message.author.id):
                if message.content.startswith(os.getenv('prefix')):
                    return
                # function to fetch an invite to the user, IF IT EXISTS!
                async def fetchInvite(user):
                    inviteChannel = User.get_invite_channel(user.id)
                    if inviteChannel == "":
                        return ""
                    try:
                        channel = bot.get_channel(int(inviteChannel))
                        if channel == None:
                            await logger.log("Channel not found! ChannelID: " + inviteChannel, bot, "WARNING")
                        invite = await channel.create_invite(max_uses=1, max_age=3600, reason="noDoot - Instant Invite for " + user.name + ". Expires in 1 hour, single use.")
                        return " You can join back to the guild you wanted to join using this link: <" + invite.url + ">!"
                    except Exception as e:
                        await logger.log("Could not generate an invite to the user ( " + user.name + " `" + str(user.id) + "`)! - " + str(e), bot, "DEBUG")
                        return ""

                # check the captcha
                captcha_text = User.get_captcha(message.author.id)

                await logger.log("User: " + message.author.name + " `" + str(message.author.id) + "` - Captcha Text: " + captcha_text + " - Message content: " + message.content, bot, "DEBUG")

                # if the message content is equals to that of the message
                if message.content == captcha_text:
                    # If the user is already verified, do nothing
                    if User.isUserVerified(message.author.id):
                        await logger.log("User tried to do captcha again, but are already verified! User: " + message.author.name, bot, "DEBUG")
                        return
                    # if not, add them to the verified db
                    User.verify_user(message.author.id)
                    # Send completion message
                    await logger.log("User completed captcha sucessfully! Added to verified users! User: " + message.author.name + " `" + str(message.author.id) + "`", bot, "INFO")
                    invite_message = await fetchInvite(message.author)
                    await message.channel.send(content="**Captcha completed successfully!**\nYour account is now verified!" + invite_message)

                    # Kick from the noDoot Server
                    try:
                        await bot.get_guild(int(os.getenv('guild'))).kick(message.author, reason="noDoot - User verified sucessfully!")
                    except Exception as e:
                        await logger.log("Not enough permissions to kick user from the noDoot Verification Guild! User: " + message.author.name + " (`" + str(message.author.id) + "`) - " + str(e), bot, "DEBUG")
                    return
                # if not
                await message.channel.send(content="**Incorrect answer! Try again...**\n*If the captcha won't work, contact HeroGamers#0001 (listed as noDoot Developer on the noDoot Verification Server)!*")

def setup(bot):
    bot.add_cog(listenerCog(bot))
