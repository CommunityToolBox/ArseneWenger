#!/usr/bin/env python
"""
A cog to spit back random lines from files
"""

import random

import discord
from discord import app_commands
from discord.ext import commands

from arsene_wenger.utils import get_timestamp


class FactsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.MANAGER_IDS = {"wenger": 51, "unai": 37569, "arteta": 51018}

    @commands.command(name="wengersucks")
    async def wenger_sucks(self, ctx):
        with open("wengerSucks.txt", encoding="utf-8") as f:
            content = f.read()

        for message in content.split("\n\n"):
            return await ctx.send(message)

    @app_commands.command(
        name="wengerfact",
        description="Get a random fact about our lord and savior Arsene Wenger.",
    )
    async def wenger_fact(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=await self.get_manager_fact("wenger"))

    @app_commands.command(
        name="unaifact",
        description="Get a random fact about our former manager Unai Emery.",
    )
    async def unai_fact(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=await self.get_manager_fact("unai"))

    @app_commands.command(
        name="artetafact",
        description="Get a random fact about our current manager Mikel Arteta",
    )
    async def arteta_fact(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=await self.get_manager_fact("arteta"))

    async def get_manager_fact(self, manager):
        """
        Get a random fact and return it as a nice embed
        :param manager:
        :return:
        """
        facts = f"facts/{manager}Facts.txt"
        try:
            with open(facts, encoding="utf-8") as f:
                content = f.readlines()

            line = random.choice(content)
            embed = discord.Embed(description=line, color=0x9C824A)

            embed.set_author(
                name=f"{manager.title()} Fact",
                icon_url=f"https://resources.premierleague.com/premierleague/photos/players/250x250/man{self.MANAGER_IDS[manager]}.png",
            )
            return embed
        except FileNotFoundError:
            print(f"{get_timestamp()}\nError reading file {facts}")


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(FactsCog(bot))
