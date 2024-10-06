from discord.ext.commands import Cog

class Test(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Test")

async def setup(bot):
    await bot.add_cog(Test(bot))
