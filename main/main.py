from lib.bot import bot
import json

openAiKey = str()
discordKey = str()
with open('keys.json') as file:
    json = json.load(file)
    openAiKey = json["openAiKey"]
    discordKey = json["discordKey"]

bot.run()