import asyncio
from glob import glob
from .chatbot_function import chat_with_gpt

import discord
from discord.ext import commands
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import cog
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)
from discord.ext.commands import Bot


intents = discord.Intents.all()
intents.message_content = True

ignore_exceptions = (CommandNotFound, BadArgument, MissingRequiredArgument)
cogs = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

class Ready: 
    def __init__(self):
        for cog in cogs:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in cogs])

class MyBot(Bot):
    def __init__(self, discordKey):
        self.ready = False
        self.guild = None
        self.cogs_ready = Ready()

        super().__init__(
            command_prefix='!',
            owner_ids=[0],
            intents=intents,
            #help_command=None,
            case_insensitive=True,
        )

        self.TOKEN = discordKey

    def setup(self):
        for cog in cogs:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")
        print("Cog setup complete")

    def run(self):
        #print(" Botsetup started")
        self.setup()

        #with open("./main/secrets/discord_token.0", "r", encoding="UTF-8") as tf:
        # self.TOKEN = 
        
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        #print("Bot connected")
        pass

    async def on_disconnect(self):
        #print("Bot disconnected")
        pass

    async def on_ready(self):
        #print("Bot is starting")
        if not self.ready:
            print("### Bot online ###") 
            pass
        else:
            print("Bot failed to connect")

        while True:
            await super().change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name="in do saily zui")
            )
            await asyncio.sleep(20)
            await super().change_presence(
                activity=discord.Activity(type=discord.ActivityType.playing, name="dookiet af pilips tisch")
            )
            await asyncio.sleep(29)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Get the user's message and generate a response
        user_input = message.content
        user_author = message.author
        response = chat_with_gpt(user_input, user_author)
        
        await message.channel.send(f"{response}")

#bot = MyBot()
