import discord
from discord.ext import tasks, commands

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=2.0)
    async def change_presence(self):
        await self.bot.change_presence(type=discord.ActivityType.watching, name="in do saily ban gaggn zui")

async def setup(bot):
    await bot.add_cog(Tasks(bot))