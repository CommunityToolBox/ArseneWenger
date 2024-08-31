#!/usr/bin/env python
"""
An example cog to show how things should be done.

Also provides a simple base for starting a new cog.
"""

import discord
from discord import app_commands

# In this case, discord import is not needed, in some cases it may be.
# import discord
from discord.ext import commands


class ExampleCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="The pong to your ping, let's you know that the bot is alive.",
    )
    async def ping(self, interaction: discord.Interaction):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        await interaction.response.send_message("Pong")


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(ExampleCog(bot))
