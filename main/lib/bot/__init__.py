import asyncio
from glob import glob
from .chatbot_function import Chatbot
import os

import discord
from discord.ext import commands
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)
from discord.ext.commands import Bot


prefix = "!"

intents = discord.Intents.all()
intents.voice_states = True
intents.message_content = True

ignore_exceptions = (CommandNotFound, BadArgument, MissingRequiredArgument)
cogs = [os.path.basename(path)[:-3] for path in glob("./main/lib/cogs/*.py")]

class Cogs: 
    def __init__(self):
        for cog in cogs:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" > {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in cogs])

class MyBot(Bot):
    def __init__(self, discordKey, command_prefix=prefix):
        self.ready = False
        self.guild = None
        self.bot_cogs = Cogs()
        self.chatbot = Chatbot()
        self.command_prefix_custom = command_prefix

        super().__init__(
            command_prefix=self.get_command_prefix,
            owner_ids=[0],
            intents=intents,
            case_insensitive=True,
        )

        self.TOKEN = discordKey

    def get_command_prefix(self, bot, message):
        return self.command_prefix_custom
    
    async def setup(self):
        print("Setup started")
        for cog in cogs:
            await self.load_extension(f"lib.cogs.{cog}")
            print(f" > {cog} cog loaded")
        print("Setup complete")
        print("Bringing up cogs")

    def run(self):
        try:
            # Prüfe, ob bereits ein Eventloop läuft
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.start_bot())
            else:
                asyncio.run(self.start_bot())
        except RuntimeError:
            # Wenn kein Eventloop vorhanden ist, starte einen neuen
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            print("Cause of shutdown: KeyboardInterrupt")
        except asyncio.CancelledError:
            print("Cause of shutdown: Connection closed")
        finally:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                    
            if loop.is_running():
                tasks= asyncio.all_tasks(loop)
                for task in tasks:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

            loop.run_until_complete(self.close())
            loop.close()

    async def start_bot(self):
        await self.setup()
        await super().start(self.TOKEN)
    
    async def close(self):
        print("Shutting down...")

    async def on_disconnect(self):
        #print("Bot disconnected")
        pass

    async def on_ready(self):
        #print("Bot is starting")
        if not self.ready:
            self.ready = True
            for cog in self.bot_cogs.__dict__.keys():
               self.bot_cogs.ready_up(cog)
            print("### Bot online ###")
            print("__________________")
            print(" ")
            pass

#bot = MyBot()
