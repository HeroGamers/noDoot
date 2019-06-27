import User
from discord.ext import commands
from utilities import logger

class administration(commands.Cog, name="Bot Administration"):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="verifyuser", aliases=["vu", "vuser"])
    @commands.is_owner()
    async def _verifyuser(self, ctx, arg):
        """Verifies a user manually"""
        userid = self.getuserid(arg)
        # verifies the user
        User.verify_user(userid)
        await logger.logCommand("Verify User", ctx)
        await ctx.send(content="✅ Sucessfully made the query!")

    @commands.command(name="unverifyuser", aliases=["uvu", "removeverify", "uverifyuser"])
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

def setup(bot):
    bot.add_cog(administration(bot))
