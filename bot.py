#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

import discord
from discord.ext import commands

from utils import getTimestamp

prefix = '!'
bot = commands.Bot(
    command_prefix='!',
    case_insensitive=True
)


def load_cogs():
    # Set cogs that require loading in a specific order
    # They will be loaded in the order of the list, followed by all
    # other cogs in the /cogs folder
    cogs = [
    ]

    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                cog_name = file[:-3]
                if cog_name not in cogs:
                    cogs.append(cog_name)

    for cog in cogs:
        try:
            bot.load_extension(f'cogs.{cog}')
            print(f'Loaded cog: {cog}')
        except commands.errors.ExtensionNotFound:
            print(f'Failed to load cog: {cog}')


@bot.event
async def on_ready():
    #set playing status
    await bot.change_presence(activity=discord.Game(name='Wengerball'))
    print('Logged on as')
    print(bot.user.name)
    print('----')

try:
    f = open('token.txt')
    token = f.readline()
    f.close()
    load_cogs()
    bot.run(token.rstrip())
except Exception as e:
    print(getTimestamp() +"setup error\n")
    print(e)
    sleep(5)
