import User, os, datetime
from discord import File
from discord.ext import tasks, commands
from utilities import logger, captchaHandler


class administration(commands.Cog, name="Bot Administration"):
    def __init__(self, bot):
        self.bot = bot
        self.check_members.start()  # pylint may see this as a no-member error, which is a false positive // pylint: disable=no-member

    @classmethod
    def getuserid(cls, arg):
        if arg.startswith("<@") and arg.endswith(">"):
            return arg.replace("<@", "").replace(">", "").replace("!", "")  # fuck you nicknames
        else:
            return arg

    @commands.command(name="adduser", aliases=["au"])
    @commands.is_owner()
    async def _adduser(self, ctx, arg):
        """Adds a user to the database"""
        userid = self.getuserid(arg)
        user = await ctx.bot.fetch_user(userid)
        # adds the user to the database, if not already existing
        await User.add_user(userid, user.name + "#" + user.discriminator, ctx.bot)
        await logger.logCommand("AddUser", ctx)
        await ctx.send(content="✅ Sucessfully made the query!")

    @commands.command(name="removeuser", aliases=["ru"])
    @commands.is_owner()
    async def _removeuser(self, ctx, arg):
        """Removes a user from the database"""
        userid = self.getuserid(arg)
        # tries to remove the user from the database
        User.remove_user(userid)
        await logger.logCommand("Remove User", ctx)
        await ctx.send(content="✅ Sucessfully made the query!")

    @commands.command(name="verifyuser", aliases=["vu", "vuser", "verify"])
    @commands.is_owner()
    async def _verifyuser(self, ctx, arg):
        """Verifies a user manually"""
        userid = self.getuserid(arg)
        user = await ctx.bot.fetch_user(userid)
        # adds the user to the database, if not already existing
        await User.add_user(userid, user.name + "#" + user.discriminator, ctx.bot)
        # verifies the user
        User.verify_user(userid)
        await logger.logCommand("Verify User", ctx)
        await ctx.send(content="✅ Sucessfully made the query!")

    @commands.command(name="unverifyuser", aliases=["uvu", "removeverify", "unverify"])
    @commands.is_owner()
    async def _unverifyuser(self, ctx, arg):
        """Removes the verification from a user"""
        userid = self.getuserid(arg)
        # unverifies the user
        User.unverify_user(userid)
        await logger.logCommand("Unverify User", ctx)
        await ctx.send(content="✅ Sucessfully made the query!")

    @commands.command(name="isverified", aliases=["iv", "isuserverified"])
    @commands.is_owner()
    async def _isverified(self, ctx, arg):
        """Returns whether a user is verified"""
        await logger.log("arg: " + str(arg), ctx.bot, "DEBUG")
        userid = self.getuserid(arg)
        await logger.log("userid: " + str(userid), ctx.bot, "DEBUG")
        # checks the user the user
        verified = User.isUserVerified(userid)
        await logger.log("verified: " + str(verified), ctx.bot, "DEBUG")
        isVerified = "The user is Not Verified!"
        if verified == True:
            isVerified = "The user is Verfied!"
        await logger.logCommand("Is User Verified", ctx)
        await ctx.send(content="✅ Sucessfully made the query! " + isVerified)

    @commands.command(name="getcaptcha", aliases=["gc", "captcha"])
    @commands.is_owner()
    async def _getcaptcha(self, ctx, arg):
        """Gets a user's current captcha"""
        userid = self.getuserid(arg)
        # gets the captcha
        captcha = User.get_captcha(userid)
        await logger.logCommand("Get Captcha", ctx)
        await ctx.send(content="✅ Sucessfully made the query! Captcha: `" + captcha + "`")

    # this part uses some code from userInteraction, so check there for comments
    @commands.command(name="fcaptcha", aliases=["forcenewcaptcha", "generatecaptcha"])
    @commands.is_owner()
    async def _fcaptcha(self, ctx, arg):
        """Generates a new captcha for a user"""
        await logger.logCommand("Force New Captcha", ctx)
        bot = self.bot
        userid = self.getuserid(arg)
        users = bot.get_guild(int(os.getenv('guild'))).members
        user = None
        for member in users:
            if member.id == int(userid):
                user = member
                break

        if user == None:
            await logger.log("Could not generate new captcha for the user, " + userid + ". User not found.", bot,
                             "ERROR")
            return

        # generate a captcha
        captcha = captchaHandler.generateCaptcha()

        # Put the captcha into the db
        User.add_captcha(user.id, captcha[1])
        await logger.log(
            "Added captcha for user: " + user.name + " (" + str(user.id) + ") to the db. Captcha_text: " + captcha[1],
            bot, "INFO")

        # send the message
        dm_channel = user.dm_channel
        if dm_channel == None:
            await user.create_dm()
            dm_channel = user.dm_channel

        appinfo = await bot.application_info()
        try:
            await dm_channel.send(
                content="A new captcha has been generated to you (the captcha may consist of **lowercase letters** and **numbers**)!\n\n" +
                        "*If the captcha is not working, write `" + os.getenv(
                    'prefix') + "newcaptcha`, to generate a new captcha, or if you are stuck, then contact " + appinfo.owner.mention + " in the noDoot Verification Server through DM's!*",
                file=File(captcha[0]))
        except Exception as e:
            await logger.log("Could not send verification to user " + str(user.id) + " - " + str(e), bot, "INFO")
            # Delete the captcha from the filesystem
            os.remove(captcha[0])
            await ctx.send(content="❎ Could not send the captcha to the user!")
            return
        await logger.log("Verification sent to user: " + str(user.id), bot, "DEBUG")
        # Delete the captcha from the filesystem
        os.remove(captcha[0])
        await ctx.send(content="✅ Sent a new captcha to the user!")

    @commands.command(name="stop", aliases=["restart", "shutdown"])
    @commands.is_owner()
    async def _stop(self, ctx):
        """Stops the bot's script"""
        await logger.logCommand("Stop", ctx)
        await ctx.send(content="✅ Stopping the bot!")
        await ctx.bot.logout()
        await ctx.bot.close()

    # Start the looped function, that checks if there are users in the noDoot Verification Guild that have been there for a veeery long time
    @tasks.loop(hours=1)
    async def check_members(self):
        await self.bot.wait_until_ready()
        logger.logDebug("Running the check_members task...", "DEBUG")
        appinfo = await self.bot.application_info()
        owner = appinfo.owner
        guild = self.bot.get_guild(int(os.getenv('guild')))
        for member in guild.members:
            time_in_guild = (datetime.datetime.now() - member.joined_at) / datetime.timedelta(hours=1)
            if member.bot:
                continue
            elif member.id == owner.id:
                continue
            elif member.guild_permissions.administrator:
                continue
            else:
                logger.logDebug("Member: " + member.name + " - " + str(time_in_guild) + " hours", "DEBUG")
                if time_in_guild > 5:  # We clean up the noDoot Verification Server for inactive users every 5 hours
                    await logger.log("Kicked member, " + member.name + " (`" + str(
                        member.id) + "`), from the noDoot Verification Server, for being there for longer than 5 hours... Total hours: " + str(
                        time_in_guild), self.bot, "INFO")
                    await member.kick(reason="noDoot - User inactive in Verification Server!")


def setup(bot):
    bot.add_cog(administration(bot))
