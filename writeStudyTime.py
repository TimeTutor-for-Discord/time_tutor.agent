from discord.ext import commands
import discord
import asyncio
import config

intents = discord.Intents.all()
TOKEN = config.Token
prefix = "¥"

# Botのインスタンスを作成
bot = commands.Bot(command_prefix=prefix, help_command=None, intents=intents)

# 拡張機能を非同期でロードする関数
async def load_extensions():
    await bot.load_extension("Cogs.default")
    await bot.load_extension("Cogs.Studyrecord.entryExit")

# メインの非同期関数を作成してBotを実行
async def main():
    await load_extensions()  # 拡張機能をロード
    await bot.start(TOKEN)  # Botを起動

# イベントループでメイン関数を実行
asyncio.run(main())
