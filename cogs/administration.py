import User, os, datetime
from discord.ext import tasks, commands
from utilities import logger

class administration(commands.Cog, name="Bot Administration"):
    def __init__(self, bot):
        self.bot = bot
        self.check_members.start() # pylint may see this as a no-member error, which is a false positive // pylint: disable=no-member

    @classmethod
    def getuserid(cls, arg):
        if arg.startswith("<@") and arg.endswith(">"):
            return arg.replace("<@", "").replace(">", "")
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
            time_in_guild = (datetime.datetime.now()-member.joined_at)/datetime.timedelta(hours=1)
            if member.bot:
                continue
            elif member.id == owner.id:
                continue
            else:
                logger.logDebug("Member: " + member.name + " - " + str(time_in_guild) + " hours", "DEBUG")
                if time_in_guild > 5: # We clean up the noDoot Verification Server for inactive users every 5 hours
                    await logger.log("Kicked member, " + member.name + " (`" + str(member.id) + "`), from the noDoot Verification Server, for being there for longer than 5 hours... Total hours: " + str(time_in_guild), self.bot, "INFO")
                    await member.kick(reason="noDoot - User inactive in Verification Server!")

def setup(bot):
    bot.add_cog(administration(bot))
