import json
import logging
import os
import sys

import discord
from discord.ext import commands

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if not os.path.isfile("config.json"):
    sys.exit("'Config file not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config['prefix'], intents=intents)

    async def startup(self):
        await bot.wait_until_ready()
        await bot.tree.sync()
        await bot.change_presence(activity=discord.Game(name='Wengerball'))
        logging.info('Successfully synced applications commands')
        logging.info(f'Connected as {bot.user}')

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    logging.info(f"Loaded {filename}")
                except Exception as e:
                    logging.error(f"Failed to load {filename}")
                    logging.error(f"[ERROR] {e}")

        self.loop.create_task(self.startup())


bot = Bot()
bot.run(config["token"])
