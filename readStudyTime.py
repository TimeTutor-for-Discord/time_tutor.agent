from discord.ext import commands
import discord

import config


intents = discord.Intents.all()
TOKEN = config.Token
prefix = "¥"

bot = commands.Bot(command_prefix=prefix, intents=intents)


bot.load_extension("Cogs.default")

bot.load_extension("Cogs.Aggregationtime.weekAggregate")
bot.load_extension("Cogs.Aggregationtime.monthAggregate")
bot.load_extension("Cogs.Aggregationtime.cronAggregate")
bot.load_extension("Cogs.Aggregationtime.personalDayRecord")
bot.load_extension("Cogs.Aggregationtime.personalWeekRecord")
bot.load_extension("Cogs.Aggregationtime.addrankrole_monthly_aggregation")


bot.run(TOKEN)
