#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog with meme commands
"""
import random

from discord.ext import commands

from utils import clamp_int


class MemeCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="wengyboi",
        help="Make a wengyboi of # length! Max 10.")
    async def makewneger(self, ctx, length: int = 1):
        length = clamp_int(length, 1, 10)

        body = '<:ArseneTop:522209469547937802>\n'
        for i in range(0, length):
            body += '<:ArseneMid:522209585403265045>\n'
        body += '<:ArseneBot:522209598464196608>\n'
        await ctx.send(body)

    @commands.command(
        name="copy"
    )
    async def copy(self, ctx):
        pastas = [
            "Right now I'm sitting outside of the Tony Adams Statue and I am still as <:moh:358216187752087552> passionate <:moh:358216187752087552> about this club as I was the first time my uncle <:ArseneTop:346679833020989440>  took me to a game in 1991. I\'m reading the engravings on the paving outside the stadium and it fills me with <:tr7:239057992928985089>  pride. Through the ups  <:ozgasm:332570750290755586> and the downs <:wut:344131531108909056> we are fucking<:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> . No matter what \"faction\" <:thethinker:337164686849998849> you may fall under we are Arsenal. If you are more concerned with <:kappa:339386429392027648> WengerOut memes or <:gaffer:344131531096457216> AKB and arguing on the internet then go find another team to support. <:laca:341950939055259650> <:laca:341950939055259650> I\'m reading the testimony of generations of people who supported this club wholeheartedly <:thierry:344131530676764682>, through good and bad. <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> We are Arsenal. <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> Never forget that <:gaffer:344131531096457216>",
            "To be fair, you have to have a very high IQ to understand Arsenal football. The tactics are extremely subtle, and without a solid grasp of the 3-4-2-1 formation most of the crosses will go over a typical striker’s head. There’s also Wenger’s nihilistic outlook, which is deftly woven into his lineup- his personal philosophy draws heavily from Herbert Chapman literature, for instance. The fans understand this stuff; they have the intellectual capacity to truly appreciate the depths of these losses, to realise that they’re not just funny- they say something deep about LIFE. As a consequence people who dislike the Arsenal truly ARE idiots- of course they wouldn’t appreciate, for instance, the humour in the Gunners’ existential catchphrase “Wenger Out!” which itself is a cryptic reference to the Invincibles Season. I’m smirking right now just imagining one of those addlepated simpletons scratching their heads in confusion as Mesut Ozil’s genius wit unfolds itself on their television screens. What fools.. how I pity them.  😂\n And yes, by the way, i DO have an Arsenal tattoo. And no, you cannot see it. It’s for the ladies’ eyes only- and even then they have to demonstrate that they’re within 5 IQ points of my own (preferably lower) beforehand. Nothin personnel kid  😎"
        ]
        await ctx.send(random.choice(pastas))


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(MemeCog(bot))
