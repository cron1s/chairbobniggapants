import discord
from discord.ext import commands
from discord.ext.commands import Bot

intents = discord.Intents.default()
intents.message_content = True

class Ready: 
    def __init__(self):
        setattr(self, False)

class MyBot(Bot):
    def __init__(self):
        self.ready = False
        self.guild = None

        super().__init__(

            command_prefix='',
            owner_ids=[0],
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )
    def setup(self):
        pass

    def run(self):
        print(" Botsetup started")
        self.setup()

        with open("./main/secrets/discord_token.0", "r", encoding="UTF-8") as tf:
            self.TOKEN = tf.read()
        
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

bot = MyBot()
