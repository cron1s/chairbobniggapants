import discord
from discord.ext import commands

# Setze deinen Bot-Token hier ein
TOKEN = 'MTI5MjE3ODIyODM3ODU5OTQ5Ng.GeFk8Z.I42S8WW4UUCDUjQioWJJHDfyXqRPx0sGmzFdKg'

# Intents erstellen und definieren, auf welche Events der Bot zugreifen darf
intents = discord.Intents.default()
intents.message_content = True  # Ermöglicht dem Bot, Nachrichteninhalte zu lesen

# Erstelle eine Instanz des Bots mit einem Kommando-Präfix und den definierten Intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Wenn der Bot bereit ist und online geht
@bot.event
async def on_ready():
    print(f'{bot.user} ist online!')

@bot.command()
async def ping(ctx):
    await ctx.send('Du bisch a grausigs orschloch du kriegsch nix fa mir')

@bot.command()
async def chairbob(ctx):
    await ctx.send('Conversational, Helpful, Adaptive, Intelligent, Responsive, Bot, Optimized, Brain, Natural, Interactive, Guided, GAN, Assistant, Personalized, Analytical, Networked, Trustworthy, Supportive')

@bot.command()
async def saily(ctx):
    await ctx.send('I bin eigentlich die Saily, du bleds orschloch')

# Bot starten
bot.run(TOKEN)

