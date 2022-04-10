#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to spit back random lines from files
"""
import discord
from discord.ext import commands
import random

from utils import getTimestamp


class FactsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.MANAGER_IDS = {
            'wenger': 51,
            'unai': 37569,
            'arteta': 51018
        }

    @commands.command(
        name="wengersucks"
    )
    async def wengerSucks(self, ctx):
        with open('wengerSucks.txt', 'r', encoding="utf-8") as f:
            content = f.read()

        for message in content.split("\n\n"):
            await ctx.send(message)

    @commands.command(
        name="wengerfact",
        help="Get a random fact about our lord and savior Arsene Wenger.")
    async def wengerFact(self, ctx):
        await ctx.send(embed=await self.getManagerFact('wenger'))

    @commands.command(
        name="unaifact",
        help="Get a random fact about our former manager Unai Emery.")
    async def unaiFact(self, ctx):
        await ctx.send(embed=await self.getManagerFact('unai'))

    @commands.command(
        name="artetafact",
        help="Get a random fact about our current manager Mikel Arteta")
    async def artetaFact(self, ctx):
        await ctx.send(embed=await self.getManagerFact('arteta'))

    async def getManagerFact(self, manager):
        """
        Get a random fact and return it as a nice embed
        :param manager:
        :return:
        """
        facts = f'facts/{manager}Facts.txt'
        try:
            with open(facts, 'r', encoding="utf-8") as f:
                content = f.readlines()

            line = random.choice(content)
            embed = discord.Embed(
                description=line,
                color=0x9C824A)

            embed.set_author(
                name=f"{manager.title()} Fact",
                icon_url=f"https://resources.premierleague.com/premierleague/photos/players/250x250/man{self.MANAGER_IDS[manager]}.png")
            return embed
        except FileNotFoundError:
            print(f"{getTimestamp()}\nError reading file {facts}")


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(FactsCog(bot))
