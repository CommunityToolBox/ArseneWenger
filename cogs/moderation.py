#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A moderation cog to automate deletion and moderation of messages
"""
import logging
import re

from discord.ext import commands

logger = logging.getLogger(__name__)

mod_roles = ['Gaffer', 'Coach', 'Captain']


def is_moderator(user):
    return any(role.name in mod_roles for role in user.roles)


class ModerationCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        with open('banned.txt', 'r', encoding="utf-8") as f:
            self.banned = f.read().splitlines()

    def check_invite(self, message_string):
        """Check if a message contains a discord invite link and return true for removal."""
        is_invite = re.search(r'\b(?:https?:\/\/)?(?:www\.)?discord\.gg\/\w+\b', message_string)
        if is_invite:
            logger.info(f'Link {is_invite.group()} in message {message_string}')
            return True
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if is_moderator(message.author):
            logger.info(f'Mods can do what they want.')
            return
        msg_lower = message.content.lower()
        if any(ele in msg_lower for ele in self.banned):
            await message.delete()
            await message.channel.send(f"Sorry {str(message.author)} that source is not allowed.")
        elif self.check_invite(msg_lower):
            await message.delete()
            await message.channel.send(f"Sorry {str(message.author)} invites are not allowed.")

    @commands.command(
        name="clear",
        help="Clears messages")
    @commands.check(lambda ctx: ctx.message.author.id == 193393269068136448)
    async def clear(self, ctx, message_count: int):
        await ctx.channel.purge(limit=message_count + 1)


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(ModerationCog(bot))
