import discord, User, os
from discord import File
from discord.ext import commands
from utilities import logger, captchaHandler

class userInteraction(commands.Cog, name="User Interaction"):
    def __init__(self, bot):
        self.bot = bot

    # this part uses some code from listenerCog, so check there for comments
    @commands.command(name="newcaptcha", aliases=["new", "nc", "ncaptcha"])
    @commands.dm_only()
    async def _newcaptcha(self, ctx):
        """[DM Only] Gets a new captcha for the user"""
        if User.isUserVerified(ctx.author.id):
            return
        await logger.logCommand("New Captcha", ctx)
        bot = self.bot
        # generate a captcha
        captcha = captchaHandler.generateCaptcha()

        # Put the captcha into the db
        User.add_captcha(ctx.author.id, captcha[1])
        await logger.log("Added captcha for user: " + ctx.author.name + " (" + str(ctx.author.id) + ") to the db. Captcha_text: " + captcha[1], bot, "INFO")

        # send the message
        appinfo = await bot.application_info()
        await logger.log("Verification sent to user: " + str(ctx.author.id), bot, "DEBUG")
        await ctx.send(content="A new captcha has been generated to you (the captcha may consist of **lowercase letters** and **numbers**)!\n\n" +
            "*If the captcha is not working, write `" + os.getenv('prefix') + "newcaptcha` again to generate a new captcha, or if you are stuck, then contact " + appinfo.owner.mention + " in the noDoot Verification Server through DM's!*", file=File(captcha[0]))
        # Delete the captcha from the filesystem
        os.remove(captcha[0])

def setup(bot):
    bot.add_cog(userInteraction(bot))
