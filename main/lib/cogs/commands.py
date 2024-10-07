from discord.ext import commands

def is_not_pinned(message):
    return not message.pinned

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello")
    async def say_hello(self, ctx):
        await ctx.send("hallöchen")

    @commands.command(name="clear")
    async def clear(self, ctx, amount: int = 99):
        if ctx.author.guild_permissions.manage_messages:
            deleted = await ctx.channel.purge(limit=amount, check=is_not_pinned)
            await ctx.send(f'{len(deleted) - 1} nochrichtn augiraumb.', delete_after=3)

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Du bisch {latency}ms hinto mir.")

async def setup(bot):
    await bot.add_cog(Commands(bot))
