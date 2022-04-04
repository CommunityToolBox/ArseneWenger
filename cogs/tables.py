# !/usr/bin/python
# -*- coding: utf-8 -*-
import re
import requests
import requests.auth

import discord
import pandas as pd
import tabulate
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

class Tables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="Table",
        help="Display the current Premier League Table."
    )
    async def leagueTable(self, ctx,
                          background: str = ''):
        body = livetable()

        # Check if (w)hite or (l)ight, else use dark mode
        light_mode = background.startswith('l') or background.startswith('w')

        bg_colour = (255, 255, 255) if light_mode else (47, 49, 54)
        font_colour = (0, 0, 0) if light_mode else (255, 255, 255)

        img = Image.new('RGB', (1130, 840), bg_colour)
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("AnonymousPro.ttf", 36)
        d.text((5, 10), body, font_colour, font=font)
        img.save('tempImg.jpg')

        await ctx.send("EPL Standings", file=discord.File('tempImg.jpg'))

    @commands.command(
        name="Europa",
        help="Display the Europa League Table."
    )
    async def europaTable(self, ctx):
        body = main()
        await ctx.send('```' + body + '```')

# Utility Functions for tables


def getSign(goalDiff):
    if int(goalDiff) > 0:
        return "+" + goalDiff
    return goalDiff


# Premier League Table


def discordAbove(table, index, i):
    body = ""
    if index < 0:
        return body
    elif index == 0:
        team = re.findall('a href=".*">(.*)<\/a>', table[1])[0]
        position = re.findall('<td class="pos">(.*)</td>', table[1])[0]
        goalDiff = re.findall('<td class="gd">(.*)</td>', table[1])[0]
        points = re.findall('<td class="pts">(.*)</td>', table[1])[0]
        body += "| " + position + " |" + team + "|" + getSign(goalDiff) + "|" + points + "|\n"
    else:
        for x in range(index, i):
            team = re.findall('a href=".*">(.*)<\/a>', table[x])[0]
            position = re.findall('<td class="pos">(.*)</td>', table[x])[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>', table[x])[0]
            points = re.findall('<td class="pts">(.*)</td>', table[x])[0]
            body += "| " + position + " |" + team + "|" + getSign(goalDiff) + "|" + points + "|\n"
    return body


def discordBelow(table, index, i):
    body = ""
    if index < 5:
        index = 5
    for x in range(i + 1, index + 1):
        team = re.findall('a href=".*">(.*)<\/a>', table[x])[0]
        position = re.findall('<td class="pos">(.*)</td>', table[x])[0]
        goalDiff = re.findall('<td class="gd">(.*)</td>', table[x])[0]
        points = re.findall('<td class="pts">(.*)</td>', table[x])[0]
        body += "| " + position + " |" + team + "|" + getSign(goalDiff) + "|" + points + "|\n"
    return body


def findArsenal(table):
    header = "| Pos |  Team  | GD | Pts |\n"
    for index, pos in enumerate(table):
        team = re.findall('a href=".*">(.*)<\/a>', pos)[0]
        if team == "Arsenal":
            i = index
            position = re.findall('<td class="pos">(.*)</td>', pos)[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>', pos)[0]
            points = re.findall('<td class="pts">(.*)</td>', pos)[0]
            body = "| " + position + " |" + team.upper() + "|" + getSign(goalDiff) + "|" + points + "|\n"
    topRange = i + 2
    botRange = i - 2
    if botRange <= 1:
        topRange += 1
    above = discordAbove(table, botRange, i)
    below = discordBelow(table, topRange, i)
    body = header + above + body + below
    return body


def parseWebsite():
    website = "https://www.espn.com/soccer/standings/_/league/eng.1"
    tableWebsite = requests.get(website, timeout=15)
    table_html = tableWebsite.text
    fullTable = table_html.split('<div class="responsive-table">')
    table = fullTable.split('<tr style="background-color:')
    # fixtures[0] now holds the next match
    return table


def shortenedClubNames(club):
    clublist = {
        "Chelsea": "Chelsea",
        "Manchester City": "Man City",
        "Brighton and Hove Albion": "Brighton",
        "Tottenham Hotspur": "Spurs",
        "Manchester United": "Man Utd",
        "West Ham United": "West Ham",
        "Everton": "Everton",
        "Wolverhampton Wanderers": "Wolves",
        "Leicester City": "Leicester",
        "Arsenal": "Arsenal",
        "Aston Villa": "Villa",
        "Crystal Palace": "Palace",
        "Southampton": "Southampton",
        "Watford": "Watford",
        "Leeds United": "Leeds",
        "Burnley": "Burnley",
        "Newcastle United": "Newcastle",
        "Norwich City": "Norwich",
        "Brentford": "Brentford",
        "Liverpool": "L'pool"
    }
    return clublist[club]


def livetable():
    tableurl = "https://www.premierleague.com/tables"
    x1 = requests.get(tableurl, stream=True)
    x2 = ""
    for lines in x1.iter_lines():
        lines_d = lines.decode('utf-8')
        x2 = x2 + lines_d
        if "tableCompetitionExplainedContainer" in lines_d:
            break
    tableslist = pd.read_html(x2)[0]
    rows = tableslist.to_numpy().tolist()
    i = 0
    data = [['#', 'Team', 'Pl', 'W', 'D', 'L', 'GD', 'Pts']]
    while i < len(rows):
        tablerow = rows[i]
        risefall = [tablerow[0].split(' ', 1)[0], tablerow[0].rsplit(' ', 1)[1]]
        print(risefall)
        if int(risefall[0]) < int(risefall[1]):
            risefallind = '^ '
        elif int(risefall[0]) > int(risefall[1]):
            risefallind = 'v '
        else:
            risefallind = '- '
        pos = risefall[0]
        fullteamname = tablerow[1].rsplit(" ", 1)[0].strip()
        team = shortenedClubNames(fullteamname)
        if team == 'Arsenal':
            pos = "-> " + pos
        pl = tablerow[2]
        w = tablerow[3]
        d = tablerow[4]
        l = tablerow[5]
        gd = tablerow[8]
        pts = tablerow[9]
        team = risefallind + team
        data.append([pos, team, pl, w, d, l, gd, pts])
        i = i + 2

    tabulate.PRESERVE_WHITESPACE = False
    table = tabulate.tabulate(data, headers='firstrow', tablefmt='pretty', colalign=('right', 'left',))
    return table

# EUROPA LEAGUE


def buildTable(table):
    body = ""
    for i in range(0,4):
        team = re.findall('a href=".*">(.*)<\/a>',table[i])[0]
        position = re.findall('<td class="pos">(.*)</td>',table[i])[0]
        goalDiff = re.findall('<td class="gd">(.*)</td>',table[i])[0]
        points = re.findall('<td class="pts">(.*)</td>',table[i])[0]
        if team == 'Arsenal':
            team = team.upper()
        body += "|"+position+"|"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    return body


def parseWebsite():
    website = "http://www.espnfc.us/uefa-europa-league/2310/group/8/group-h"
    tableWebsite = requests.get(website, timeout=15)
    table_html = tableWebsite.text
    table = table_html.split('<tr style="background-color:')[1:]
    return table


def main():
    table = parseWebsite()
    body = buildTable(table)
    return body


def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    bot.add_cog(Tables(bot))
