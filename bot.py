#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import asyncio
from time import sleep

import discord
from discord.ext import commands

from utils import getTimestamp

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

prefix = '!'
bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
    intents=intents
)


async def load_cogs() -> None:
    # Set cogs that require loading in a specific order
    # They will be loaded in the order of the list, followed by all
    # other cogs in the /cogs folder

    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                cog_name = file[:-3]
                try:
                    await bot.load_extension(f'cogs.{cog_name}')
                    print(f'Loaded cog: {cog_name}')
                except commands.errors.ExtensionNotFound:
                    print(f'Failed to load cog: {cog_name}')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Wengerball'))
    print('Logged on as')
    print(bot.user.name)
    print('----')

try:
    f = open('token.txt')
    token = f.readline()
    f.close()
except Exception as e:
    print(getTimestamp() +"setup error\n")
    print(e)
    sleep(5)

asyncio.run(load_cogs())
bot.run(token)
