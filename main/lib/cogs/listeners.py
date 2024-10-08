from discord.ext import commands

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1292199193380782120

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        command_prefix = self.bot.command_prefix_custom

        if message.content.startswith(command_prefix):
            return 

        if message.channel.id == self.channel_id:
            user_input = message.content
            user_author = message.author.name if message.author.name is not None else message.author.name
            response = self.bot.chatbot.chat(user_input, user_author)
            await message.channel.send(f"{response}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Listeners(bot))