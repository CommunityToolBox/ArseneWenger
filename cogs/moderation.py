#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A moderation cog to automate deletion and moderation of messages
"""
from discord.ext import commands


class ModerationCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        with open('banned.txt', 'r', encoding="utf-8") as f:
            self.banned = f.read().splitlines()

    @commands.Cog.listener()
    async def on_message(self, message):
        msgLower = message.content.lower()
        if any(ele in msgLower for ele in self.banned):
            await message.delete()
            await message.channel.send(f"Sorry {str(message.author)} that source is not allowed.")

    @commands.command(
        name="clear",
        help="Clears messages")
    @commands.check(lambda ctx: ctx.message.author.id == 193393269068136448)
    async def clear(self, ctx, message_count: int):
        await ctx.channel.purge(limit=message_count + 1)


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(ModerationCog(bot))
