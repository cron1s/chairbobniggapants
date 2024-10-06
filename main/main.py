#from lib.bot import bot
from lib.bot import MyBot
import json

discordKey = str()
with open('main/keys.json') as file:
    json = json.load(file)
    discordKey = json["discordKey"]

bot = MyBot(discordKey)
bot.run()