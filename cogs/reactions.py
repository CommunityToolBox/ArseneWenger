#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple cog that adds certain reactions to messages
"""
from discord.ext import commands


class ReactionsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.reactions = {
            'tottenham': '\U0001F4A9',
            'spurs': '\U0001F4A9',
            'spuds': '\U0001F4A9',
            'mustafi': ['🔙', '🔛', '🔝'],
            '<:ornstein:346679834501709824>': ['❤', 'ozgasm:332570750290755586'],
            'brexit': 'brexit:521984465132847104',
            '<:feelsarsenalman:522208659443417099>': 'feelsarsenalman:522208659443417099',
            '<:feelsinvincibleman:375919858845483008>': ':feelsinvincibleman:375919858845483008',
            '<:nelson:346679834090668034>': 'Bossielny:346679834535264257',
            'sanchez': 'rekt:406186499802136597'
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        for content, reaction in self.reactions.items():
            if content in message.content.lower():
                if type(reaction) is list:
                    for element in reaction:
                        await message.add_reaction(element)
                else:
                    await message.add_reaction(reaction)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(ReactionsCog(bot))
