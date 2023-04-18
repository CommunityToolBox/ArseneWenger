import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="", intents=intents)

    async def startup(self):
        await bot.wait_until_ready()
        await bot.tree.sync()
        print('Successfully synced applications commands')
        print(f'Connected as {bot.user}')

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}")
                    print(f"[ERROR] {e}")

        self.loop.create_task(self.startup())
try:
    f = open('token.txt')
    token = f.readline()
    f.close()
    bot = Bot()
    bot.run(token)
except Exception as e:
    print(e)
