import discord
import random
from discord.ext import tasks, commands

class ChangeActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=30.0)
    async def change_activity(self):
        activities = [
            discord.CustomActivity("🧼 Putzt die Tische"),
            discord.CustomActivity("🧹 Kehrt in Boden"),
            discord.CustomActivity("💩 Schaug in do saily ban gaggn zui"),
            discord.CustomActivity("🤌 Schaug die Wallischen beas un"),
            discord.CustomActivity("🤦‍♀️ Loust wos die Saily wellan Bleidsinn red"),
            discord.CustomActivity("🃏 Giwingt in an Watt-Turnier"),
            discord.CustomActivity("💃 Tonzt mitn Ernst an Wolza"),
            discord.CustomActivity("🚽 Poliert die goldigen Klos"),
            discord.CustomActivity("🌿 Racht hoamla an Dübel"),
        ]
        await self.bot.change_presence(status=discord.Status.online, activity=random.choice(activities))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.change_activity.start()

async def setup(bot):
    await bot.add_cog(ChangeActivity(bot))