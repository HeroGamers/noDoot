import discord, User, datetime
from discord.ext import commands
from utilities import logger

class info(commands.Cog, name="Information"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=["info"])
    async def _botinfo(self, ctx):
        """Gets information about the bot"""
        embed = discord.Embed(title="noDoot Bot Information", color=discord.Color.from_rgb(114, 137, 218), timestamp=datetime.datetime.now(),
            description="The bot is currently in `%s` guilds, with a total of `%s` users!" % (len(ctx.bot.guilds), len(ctx.bot.users)))
        embed.add_field(name="Verified users", value="%s" % User.count_verified_users(), inline=True)
        await logger.logCommand("Bot Info", ctx)
        await ctx.send(embed=embed)

    @commands.command(name="invite", aliases=["inv", "botinvite", "botinv"])
    async def _invite(self, ctx):
        """Sends OAuth 2 links to add the bot"""
        await logger.logCommand("Bot Invite", ctx)
        await ctx.send("To invite the bot to your server, click one of the following links:\n\n" +
            "**[Recommended Option]:**\nWith Create Instant Invite Permissions: <https://discordapp.com/oauth2/authorize?client_id=592829567660457985&scope=bot&permissions=3>\n" +
            "**[Not Recommended Option]:**\nWithout Create Instant Invite Permissions: <https://discordapp.com/oauth2/authorize?client_id=592829567660457985&scope=bot&permissions=2>\n\n" +
            "**Notice:**\n*The Kick Members Permissions is required, but can be given through other roles if wanted. The Create Instant Invite Permissions is optional, but is required if you want the bot to give the user a new invite back to the server they tried to join, if kicked. It is highly recommended to turn off the random welcome messages, as the bot will not delete those after a possible kick.*")

    @commands.command(name="feedback", aliases=["support"])
    async def _feedback(self, ctx):
        """Leave feedback or get support regarding the bot"""
        await logger.logCommand("Bot Feedback/Support", ctx)
        await ctx.send("**Hello there!**\n" +
            "To leave Feedback and/or get Support regarding the bot, please reach out to HeroGamers#0001's DM's, or through Treeland:\n" +
            "<https://discord.gg/PvFPEfd>")

    @commands.command(name="source", aliases=["sourcecode", "github", "git"])
    async def _source(self, ctx):
        """Sends a link to the bot's GitHub page"""
        await logger.logCommand("Source Code", ctx)
        await ctx.send("More sauce, please! Oh, you asked for the source? Well, did you know that noDoot is an Open Sourced bot, and that means that yo~ ..oh, you just wanted the link..? W-w-well here you go, you can view my code at:\n" +
            "https://github.com/Fido2603/noDoot")

def setup(bot):
    bot.add_cog(info(bot))
