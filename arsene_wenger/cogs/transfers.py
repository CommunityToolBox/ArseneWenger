#!/usr/bin/env python
"""
A cog to get transfers
"""

from datetime import date

import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class TransfersCogs(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @commands.command(
        name="anysignings",
        help="Get Arsenal signings for the current transfer window/season",
    )
    async def signings(self, ctx):
        players = ""
        if "None" not in get_signings():
            for name in get_signings():
                players += name + "\n"
        else:
            players = "Fuck All"
        await ctx.send(players)


def get_signings():
    """
    Grab any signings made during the current transfer window
    """
    transfers = []
    current_date = date.today()
    year = current_date.year
    if current_date.month < 5:
        year -= 1
    if current_date.month <= 2:
        season = "w"
    elif 5 <= current_date.month <= 9:
        season = "s"
    else:
        season = ""
    address = (
        "https://www.transfermarkt.us/arsenal-fc/transfers/verein/11/plus/1?saison_id="
        + str(year)
        + "&pos=&detailpos=&w_s="
        + season
    )
    website = requests.get(address, headers={"User-Agent": "Custom"})
    soup = BeautifulSoup(website.text, "lxml")
    soup = soup.findAll("div", {"class": "box"})[2]
    table = soup.find("div", {"class": "responsive-table"})
    table = table.find("tbody")
    status = ""
    if table is None:
        return ["None"]
    for row in table.findAll("tr", {"class": ["odd", "even"]}):
        try:
            status = row.find("td", {"class": "rechts hauptlink"}).find_all("a", href=True)[0].getText()
        except AttributeError:
            print("blank row")
        if "End of loan" not in status:
            transfers.append(row.find("td", {"class": "hauptlink"}).find_all("a", href=True)[0].getText())
    return transfers


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(TransfersCogs(bot))
