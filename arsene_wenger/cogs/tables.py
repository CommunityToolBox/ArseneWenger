# !/usr/bin/python
import re

import discord
import pandas as pd
import requests
import requests.auth
import tabulate
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class Tables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="table", description="Display the current Premier League Table.")
    async def league_table(self, interaction: discord.Interaction, background: str = ""):
        body = livetable()

        # Check if (w)hite or (l)ight, else use dark mode
        light_mode = background.startswith("l") or background.startswith("w")

        if light_mode:
            return await interaction.response.send_message("Light mode is not allowed, you spud.")

        bg_colour = (47, 49, 54)
        font_colour = (255, 255, 255)

        img = Image.new("RGB", (1130, 840), bg_colour)
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("arsene_wenger/AnonymousPro.ttf", 36)
        d.text((5, 10), body, font_colour, font=font)
        img.save("tempImg.jpg")

        await interaction.response.send_message("EPL Standings", file=discord.File("tempImg.jpg"))

    @commands.command(name="Europa", help="Display the Europa League Table.")
    async def europa_table(self, ctx):
        body = main()
        await ctx.send("```" + body + "```")


# Utility Functions for tables


def get_sign(goal_diff):
    if int(goal_diff) > 0:
        return "+" + goal_diff
    return goal_diff


# Premier League Table


def discord_above(table, index, i):
    body = ""
    if index < 0:
        return body
    elif index == 0:
        team = re.findall('a href=".*">(.*)<\/a>', table[1])[0]
        position = re.findall('<td class="pos">(.*)</td>', table[1])[0]
        goal_diff = re.findall('<td class="gd">(.*)</td>', table[1])[0]
        points = re.findall('<td class="pts">(.*)</td>', table[1])[0]
        body += "| " + position + " |" + team + "|" + get_sign(goal_diff) + "|" + points + "|\n"
    else:
        for x in range(index, i):
            team = re.findall('a href=".*">(.*)<\/a>', table[x])[0]
            position = re.findall('<td class="pos">(.*)</td>', table[x])[0]
            goal_diff = re.findall('<td class="gd">(.*)</td>', table[x])[0]
            points = re.findall('<td class="pts">(.*)</td>', table[x])[0]
            body += "| " + position + " |" + team + "|" + get_sign(goal_diff) + "|" + points + "|\n"
    return body


def discord_below(table, index, i):
    body = ""
    if index < 5:
        index = 5
    for x in range(i + 1, index + 1):
        team = re.findall('a href=".*">(.*)<\/a>', table[x])[0]
        position = re.findall('<td class="pos">(.*)</td>', table[x])[0]
        goal_diff = re.findall('<td class="gd">(.*)</td>', table[x])[0]
        points = re.findall('<td class="pts">(.*)</td>', table[x])[0]
        body += "| " + position + " |" + team + "|" + get_sign(goal_diff) + "|" + points + "|\n"
    return body


def find_arsenal(table):
    header = "| Pos |  Team  | GD | Pts |\n"
    for index, pos in enumerate(table):
        team = re.findall('a href=".*">(.*)<\/a>', pos)[0]
        if team == "Arsenal":
            i = index
            position = re.findall('<td class="pos">(.*)</td>', pos)[0]
            goal_diff = re.findall('<td class="gd">(.*)</td>', pos)[0]
            points = re.findall('<td class="pts">(.*)</td>', pos)[0]
            body = "| " + position + " |" + team.upper() + "|" + get_sign(goal_diff) + "|" + points + "|\n"
    top_range = i + 2
    bot_range = i - 2
    if bot_range <= 1:
        top_range += 1
    above = discord_above(table, bot_range, i)
    below = discord_below(table, top_range, i)
    body = header + above + body + below
    return body


def parse_website():
    website = "https://www.espn.com/soccer/standings/_/league/eng.1"
    table_website = requests.get(website, timeout=15)
    table_html = table_website.text
    full_table = table_html.split('<div class="responsive-table">')
    table = full_table.split('<tr style="background-color:')
    # fixtures[0] now holds the next match
    return table


def shortened_club_names(club):
    club_list = {
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
        "Liverpool": "L'pool",
        "Fulham": "Fulham",
        "Nottingham Forest": "Forest",
        "Bournemouth": "Bournemouth",
    }
    return club_list.get(club, club)


def livetable():
    tableurl = "https://www.premierleague.com/tables"
    x1 = requests.get(tableurl, stream=True)
    x2 = ""
    for lines in x1.iter_lines():
        lines_d = lines.decode("utf-8")
        x2 = x2 + lines_d
        if "tableCompetitionExplainedContainer" in lines_d:
            break
    tableslist = pd.read_html(x2)[0]
    rows = tableslist.to_numpy().tolist()
    i = 0
    data = [["#", "Team", "Pl", "W", "D", "L", "GD", "Pts"]]
    while i < len(rows):
        tablerow = rows[i]
        risefall = [tablerow[0].split(" ", 1)[0], tablerow[0].rsplit(" ", 1)[1]]
        if int(risefall[0]) < int(risefall[1]):
            risefallind = "^ "
        elif int(risefall[0]) > int(risefall[1]):
            risefallind = "v "
        else:
            risefallind = "- "
        pos = risefall[0]
        fullteamname = tablerow[1].rsplit(" ", 1)[0].strip()
        team = shortened_club_names(fullteamname)
        if team == "Arsenal":
            pos = "-> " + pos
        pl = tablerow[2]
        wins = tablerow[3]
        draws = tablerow[4]
        losses = tablerow[5]
        gd = tablerow[8]
        pts = tablerow[9]
        team = risefallind + team
        data.append([pos, team, pl, wins, draws, losses, gd, pts])
        i = i + 2

    tabulate.PRESERVE_WHITESPACE = False
    table = tabulate.tabulate(
        data,
        headers="firstrow",
        tablefmt="pretty",
        colalign=(
            "right",
            "left",
        ),
    )
    return table


# EUROPA LEAGUE


def build_table(table):
    body = ""
    for i in range(0, 4):
        team = re.findall('a href=".*">(.*)<\/a>', table[i])[0]
        position = re.findall('<td class="pos">(.*)</td>', table[i])[0]
        goal_diff = re.findall('<td class="gd">(.*)</td>', table[i])[0]
        points = re.findall('<td class="pts">(.*)</td>', table[i])[0]
        if team == "Arsenal":
            team = team.upper()
        body += "|" + position + "|" + team + "|" + get_sign(goal_diff) + "|" + points + "|\n"
    return body


def main():
    table = parse_website()
    body = build_table(table)
    return body


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(Tables(bot))
