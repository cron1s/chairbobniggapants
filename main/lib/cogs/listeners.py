from discord.ext import commands

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1292199193380782120

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        ctx = await self.get_context(message)

        if ctx.command is not None:
            await self.process_commands(message)
        else:
            if message.channel.id == self.channel_id:
            # Get the user's message and generate a response
                user_input = message.content
                user_author = message.author.name if message.author.nick is None else message.author.nick
                print(user_author)
                response = self.chatbot.chat(user_input, user_author)
                await message.channel.send(f"{response}")
            else:
                pass

async def setup(bot):
    await bot.add_cog(Listeners(bot))