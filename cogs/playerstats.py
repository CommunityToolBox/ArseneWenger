#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog to give interesting player facts
"""
import re
from datetime import datetime

import discord
import pandas as pd
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from tabulate import tabulate


class PlayerStatsCog(commands.Cog):
    """The ping to your pong"""

    def __init__(self, bot):
        self.bot = bot

        self.CLUB_ID_TRANSLATIONS = {
            # 'team': ['club_id', 'icon_url']
            'arsenal': ['18bb7c10', 'https://resources.premierleague.com/premierleague/badges/50/t3.png'],
            'chelsea': ['cff3d9bb', 'https://resources.premierleague.com/premierleague/badges/50/t8.png'],
            'spurs': ['361ca564', 'https://em-content.zobj.net/thumbs/120/twitter/322/pile-of-poo_1f4a9.png'],
            'united': ['19538871', 'https://resources.premierleague.com/premierleague/badges/50/t1.png'],
            'brentford': ['cd051869', 'https://resources.premierleague.com/premierleague/badges/50/t94.png'],
            'liverpool' : ['822bd0ba', 'https://resources.premierleague.com/premierleague/badges/50/t14.png'],
            'city': ['b8fd03ef', 'https://resources.premierleague.com/premierleague/badges/50/t43.png'],
            'brighton': ['d07537b9', 'https://resources.premierleague.com/premierleague/badges/50/t36.png'],
            'leeds': ['5bfb9659', 'https://resources.premierleague.com/premierleague/badges/50/t2.png'],
            'fulham': ['fd962109', 'https://resources.premierleague.com/premierleague/badges/50/t54.png'],
            'newcastle': ['b2b47a98', 'https://resources.premierleague.com/premierleague/badges/50/t4.png'],
            'southampton': ['33c895d4', 'https://resources.premierleague.com/premierleague/badges/50/t20.png'],
            'bournemouth': ['4ba7cbea', 'https://resources.premierleague.com/premierleague/badges/50/t91.png'],
            'wolves': ['8cec06e1', 'https://resources.premierleague.com/premierleague/badges/50/t39.png'],
            'palace': ['47c64c55', 'https://resources.premierleague.com/premierleague/badges/50/t31.png'],
            'everton': ['d3fd31cc', 'https://resources.premierleague.com/premierleague/badges/50/t11.png'],
            'villa': ['8602292d', 'https://resources.premierleague.com/premierleague/badges/50/t7.png'],
            'west ham': ['7c21e445', 'https://resources.premierleague.com/premierleague/badges/50/t21.png'],
            'forest': ['e4a775cb', 'https://resources.premierleague.com/premierleague/badges/50/t17.png'],
            'leicester': ['a2d435b3', 'https://resources.premierleague.com/premierleague/badges/50/t13.png']
            }

        self.COMPETITION_TRANSLATIONS = {
            'pl': 'Premier League',
            'all': 'Combined',
            'fa': 'FA Cup',
            'efl': 'EFL Cup'
        }

    @app_commands.command()
    async def goals(self, interaction: discord.Interaction, team: str = 'Arsenal'):
        if team.lower() not in self.CLUB_ID_TRANSLATIONS:
            return await interaction.response.send_message(f'Sorry, I couldn\'t find a team with the name {team},\n'
                                  f'allowed values are [{", ".join(name.title() for name in self.CLUB_ID_TRANSLATIONS.keys())}]')

        team_id = self.CLUB_ID_TRANSLATIONS[team.lower()][0]
        try:
            goals = getGoalsScored(team_id)
        except AttributeError: 
            goals = f"could not find goals for {team}"

        embed = discord.Embed(
            color=0x9C824A,
            description=f"```{goals}```"
        )
        embed.set_author(
            name=f"Top Goalscorers for {team.title()}",
            icon_url=self.CLUB_ID_TRANSLATIONS[team.lower()][1]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def assists(self, interaction: discord.Interaction, competition: str = 'pl'):
        if competition.lower() not in self.COMPETITION_TRANSLATIONS:
            return await interaction.response.send_message(f'Sorry, I couldn\'t find a competition with the name {competition}, '
                                  f'allowed values are [{", ".join(name.upper() for name in self.COMPETITION_TRANSLATIONS.keys())}]')

        competition_name = self.COMPETITION_TRANSLATIONS[competition.lower()]
        assists = getAssists(competition_name)
        embed = discord.Embed(
            color=0x9C824A,
            description=f"```{assists}```"
        )
        embed.set_author(
            name=f"Top assists for Arsenal",
            icon_url=self.CLUB_ID_TRANSLATIONS['arsenal'][1]
        )

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command()
    async def injuries(self, interaction: discord.Interaction, team: str = 'Arsenal'):
        if team != "Arsenal":
            return await interaction.response.send_message("Sorry, currently only Arsenal injuries can be seen.  Stay tuned for other teams")
        injuries = getInjuries(team)
        embed = discord.Embed(
            color=0x9C824A,
            title=f"Injuries for {team.title()}"
        )
        for i in injuries:
            embed.add_field(name=f'**{i["Player"]}**', value=f"> Reason: *{i['Reason']}*\n> Further Detail: *{i['FurtherDetail']}*\n> Potential Return: *{i['PotentialReturn']}*\n> Condition: *{i['Condition']}*\n> Status: *{i['Status']}*", inline=False)
        await interaction.response.send_message(embed=embed)

def getPlayerStats(club_id):
    top_scorer = dict()
    metrics_wanted = {"goals"}  # Can be expanded to other metrics like assists, minutes played etc
    page = requests.get(f'https://fbref.com/en/squads/{club_id}')
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
    df_topscorers = getPlayerStats(club)
    df_topscorers['goals'] = pd.to_numeric(df_topscorers['goals'])
    df_topscorers = df_topscorers.sort_values(['goals'], ascending=False).head(10)
    df_topscorers.index = df_topscorers.index + 1
    table = tabulate(df_topscorers, tablefmt='plain', colalign=['left', 'left'], showindex=False)
    return table


def getAssists(comp):
    tableurl = "https://fbref.com/en/squads/18bb7c10/2022-2023/all_comps/Arsenal-Stats-All-Competitions"
    x1 = requests.get(tableurl, stream=True)
    x2 = ""
    ind = False
    for lines in x1.iter_lines():
        lines_d = lines.decode('utf-8')
        if "div_stats_player_summary" in lines_d:
            ind = True
        if ind:
            x2 = x2 + lines_d
        if "tfooter_stats_player_summary" in lines_d:
            break

    tableslist = pd.read_html(x2)[0]
    sorted_table = tableslist.sort_values([(comp, 'Ast')], ascending=False)
    sub_table = sorted_table[[('Unnamed: 0_level_0', 'Player'), (comp, 'Ast')]].to_numpy().tolist()[0:10]
    for i in sub_table:
        i[1] = int(i[1])
    tabulate.PRESERVE_WHITESPACE = False
    table = tabulate(sub_table, tablefmt='plain', colalign=('left', 'right',))
    return table

def getInjuries(team="Arsenal"):
    tableurl = "https://www.premierinjuries.com/injury-table.php"
    #get table and convert to dataframe
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    injuries = []
    r = requests.get(tableurl).text
    bs_obj = BeautifulSoup(r, features="lxml")
    #currently team_1 is arsenal, but ideally i'd like to have some sort of error-checky way
    # to make sure that it looks for arsenal and confirms that the team ID is 1.  
    #i'll let future ren figure that out
    fullTable = bs_obj.find_all('tr', attrs={'class': "player-row team_1"})
    playerList = [i.text for i in fullTable]
    for plObj in playerList:
        playerDict = {"Player": "", "Reason": "", "FurtherDetail": "", "PotentialReturn": "", "Condition": "", "Status": ""}
        plObj = plObj.split('\n')
        plObj.pop(0)
        player = plObj.pop(0)
        playerDict["Player"] = player.rsplit("Player")[-1]
        reason = plObj.pop(0)
        playerDict["Reason"] = reason.rsplit("Reason")[-1]
        furtherDetail = plObj.pop(0)
        playerDict["FurtherDetail"] = furtherDetail.rsplit("Further Detail")[-1]
        potentialReturn = plObj.pop(0)
        # dates are in dd/mm/yyyy, AKA the correct way :D
        returnDate = potentialReturn.rsplit("Potential Return")[-1]
        if returnDate != "No Return Date":
            returnDate = datetime.strptime(returnDate, '%d/%m/%Y')
            playerDict["PotentialReturn"] = returnDate.strftime("%d-%B-%Y")
        else:
            playerDict["PotentialReturn"] = returnDate
        condition = plObj.pop(0)
        playerDict["Condition"] = condition.rsplit("Condition")[-1]
        status = plObj.pop(0)
        playerDict["Status"] = status.rsplit("Status")[-1]
        injuries += [playerDict]
    return injuries
    

async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(PlayerStatsCog(bot))
