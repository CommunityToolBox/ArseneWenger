#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to give interesting player facts
"""
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from tabulate import tabulate

from discord.ext import commands


class PlayerStatsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

        self.CLUB_ID_TRANSLATIONS = {
            'arsenal': '18bb7c10',
            'chelsea': 'cff3d9bb',
            'spurs': '361ca564'
        }

    @commands.command(
        name="goals",
        help="Get highest goalscorers for a specific team, defaults to Arsenal.")
    async def goals(self, ctx, team: str = 'Arsenal'):
        """
        Create a simple ping pong command.

        This command adds some help text and also required that the user
        have the Member role, this is case-sensitive.
        """
        if team.lower() not in self.CLUB_ID_TRANSLATIONS:
            return await ctx.send(f'Sorry, I couldn\'t find a team with the name {team}')

        team_id = self.CLUB_ID_TRANSLATIONS[team.lower()]

        await ctx.send('```'+getGoalsScored(team_id)+'```')


def getPlayerStats(club_id):
    top_scorer = dict()
    metrics_wanted = {"goals"}  # Can be expanded to other metrics like assists, minutes played etc
    page = requests.get(f'https://fbref.com/en/squads/{club_id}')  # TODO: add a config file and store club->id mapping
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", page.text), 'lxml')
    all_tables = soup.findAll("tbody")
    stats_table = all_tables[0]
    rows_player = stats_table.find_all('tr')

    for each in rows_player:
        if (each.find('th', {"scope": "row"}) != None):
            name = each.find('th', {"data-stat": "player"}).text.strip().encode().decode("utf-8")
            if 'player' in top_scorer:
                top_scorer['player'].append(name)
            else:
                top_scorer['player'] = [name]
            for f in metrics_wanted:
                cell = each.find("td", {"data-stat": f})
                a = cell.text.strip().encode()
                text = a.decode("utf-8")
                if f in top_scorer:
                    top_scorer[f].append(text)
                else:
                    top_scorer[f] = [text]
    df_topscorers = pd.DataFrame.from_dict(top_scorer)
    return df_topscorers


def getGoalsScored(club):
    df_topscorers = getPlayerStats(club).sort_values(by=['goals'], ascending=False, ignore_index=True).head(5)
    df_topscorers.index = df_topscorers.index + 1
    table = tabulate(df_topscorers, tablefmt='plain', colalign=['left', 'left'], showindex=False)
    return table


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(PlayerStatsCog(bot))
