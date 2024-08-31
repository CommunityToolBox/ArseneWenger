#!/usr/bin/env python
"""
A cog with useful commands around fixtures
"""

from datetime import date, datetime, timedelta

import discord
import requests
import requests.auth
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from fotmob import fotmob

if __name__ != "__main__":
    from arsene_wenger.utils import clamp_int


class FixturesCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    async def generate_fixtures_embed(self, interaction: discord.Interaction, team_type: str, count: int = 3):
        count = clamp_int(count, 1, 10)
        fixtures = parse_arsenal(team_type)
        fixture_list = find_fixtures(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        team_name = get_team_name(team_type)
        embed.set_author(
            name=f"Next {len(fixture_list)} {team_name} Fixtures",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png",
        )

        for fixture in fixture_list:
            embed.add_field(
                name=f"{fixture.team} - {fixture.comp}",
                value=f"{fixture.date} {fixture.time}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="fixtures", description="Display the next N fixtures, default 3, max 10.")
    async def fixtures(self, interaction: discord.Interaction, count: int = 3):
        # defer
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "", count)

    @app_commands.command(
        name="wfixtures",
        description="Display the next N fixtures for women's team, default 3, max 10.",
    )
    async def wfixtures(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "women", count)

    async def generate_next_embed(self, interaction: discord.Interaction, team_type: str):
        """generates the embed for the next and wnext commands"""
        fixtures = parse_arsenal(team_type)
        fixture = find_fixtures(fixtures, 1)[0]
        if (date.today()).month == 12 and "jan" in fixture.date.lower():
            next_match_date = f"""{fixture.date} {date.today().year+1}  {fixture.time}"""
        else:
            next_match_date = f"""{fixture.date} {(date.today()).year}  {fixture.time}"""

        # next_match_date example: Wed Nov 29 2023 20:00
        date_object = datetime.strptime(next_match_date, "%a %b %d %Y %H:%M")
        if bst_flag():
            delta = date_object - (datetime.utcnow() + timedelta(hours=1))
        else:
            delta = date_object - datetime.utcnow()

        if delta.days > 0:
            response = (
                f"Next match is {fixture.team} in {delta.days} days, {delta.seconds//3600} hours, "
                f"{(delta.seconds//60)%60} minutes"
            )
        elif delta.days == 0:
            response = f"Next match is {fixture.team} in {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes"
        else:
            channel = discord.utils.get(interaction.guild.text_channels, name="live-games")
            response = f"There is a match playing right now! head over to <#{channel.id}>"

        embed = discord.Embed(color=0x9C824A, description=response)

        team_name = get_team_name(team_type)
        embed.set_author(
            name=f"Next {team_name} Game",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png",
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="next",
        description="Display the time between now in utc and the next men's match.",
    )
    async def next(self, interaction: discord.Interaction):
        """Returns how many days, hours, and minutes are left until the next fixture"""
        # defer the response so that we don't get an unknown interaction error if it takes longer than 3 seconds
        await interaction.response.defer()
        # now we can generate the embed
        await self.generate_next_embed(interaction, "")

    @app_commands.command(
        name="wnext",
        description="Display the time between now in utc and the next women's match.",
    )
    async def wnext(self, interaction: discord.Interaction):
        """Returns how many days, hours, and minutes are left until the next women's fixture"""
        # defer the response so that we don't get an unknown interaction error if it takes longer than 3 seconds
        await interaction.response.defer()
        # now we can generate the embed
        await self.generate_next_embed(interaction, "women")

    async def generate_results_embed(self, interaction: discord.Interaction, team_type: str, count: int = 3):
        count = clamp_int(count, 1, 10)
        fixtures = parse_arsenal(team_type)
        result_list = find_results(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        embed.set_author(
            name=f"Last {len(result_list)} results",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png",
        )

        for result in result_list:
            # add green check mark if won, red x if lost, light gray circle if draw
            if result.wonOrLost == "W":
                icon = "✅"
            elif result.wonOrLost == "L":
                icon = "❌"
            else:
                icon = "⬜"

            embed.add_field(
                name=f"{icon} against {result.team} - {result.comp}",
                value=f"{result.date} {result.time} | {result.score} | ",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="results", description="Show Recent Men's Results")
    async def results(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_results_embed(interaction, "", count)

    @app_commands.command(name="wresults", description="Show Recent Women's Results")
    async def wresults(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_results_embed(interaction, "women", count)

    @commands.command(name="euro", aliases=("euros",), help="Show recent results")
    async def euro(self, ctx):
        body = get_international_cup()
        await ctx.send(f"```{body}```")

    @commands.command(name="copa", aliases=("copas",), help="Show results")
    async def copa(self, ctx):
        body = get_international_cup(44, 20210710)
        await ctx.send(f"```{body}```")

    @commands.command(name="olympic", aliases=("olympics",), help="Show results")
    async def olympic(self, ctx):
        body = get_international_cup(66, 20210810)
        body = "Men:\n" + body
        await ctx.send(f"```{body}```")
        body = get_international_cup(65, 20210810)
        body = "Women:\n" + body
        await ctx.send(f"```{body}```")


i = 0


class Match:
    def __init__(self, date, time, team, comp):
        self.date = date
        self.time = time
        self.team = team
        self.comp = comp


class Result:
    def __init__(self, date, time, team, comp, score, won_or_lost):
        self.date = date
        self.time = time
        self.team = team
        self.comp = comp
        self.score = score
        self.wonOrLost = won_or_lost


def get_team_name(team_type: str):
    """returns the team name based on the team type"""
    team_name = "Women's" if team_type == "women" else "Men's"
    return team_name


def get_location(line):
    home_team = line[0].text.strip()
    if "Arsenal" in home_team:
        return 0
    else:
        return 1


def bst_flag():
    """returns true if we are in bst"""
    date_plus_7 = datetime.utcnow().date() + timedelta(days=7)
    # BST falls between the last Sunday of march and the last sunday of october.
    return (
        3 < (datetime.utcnow().date()).month < 11
        or (datetime.utcnow().date()).month == 3
        and (3 < date_plus_7.month < 11)
    )


def parse_arsenal(gender="men"):
    """Gets the current arsenal fixtures"""
    if gender == "women":
        url = "https://www.arsenal.com/results-and-fixtures-list?field_arsenal_team_target_id=5"
    else:
        url = "https://www.arsenal.com/results-and-fixtures-list?"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    }

    # Example Table Class:
    response = requests.get(url, timeout=15, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    table = soup.select_one('div[class*="results-fixure--slimline"]')
    # find all table class="cols-0"
    matches = table.findAll("table", attrs={"class": "cols-0"})
    return matches


def find_results(matches, number: int = 3):
    """takes the matches and returns the previous number of results"""
    results = []
    # reverse matches so we're working backwards
    matches.reverse()
    for match in matches:
        match_month = match.text.split("\n\n")[1].strip()
        match_month = datetime.strptime(match_month, "%B %Y")
        current_date = datetime.utcnow()
        if (
            match_month.year > current_date.year
            or current_date.month < match_month.month
            or (
                match_month.year == current_date.year
                and current_date.month == match_month.month
                and current_date.day < match_month.day
            )
        ):
            continue
        # the rest can be split by \n\n\n
        results_array = match.text.split("\n\n\n")
        results_array.pop(0)
        results_array.pop(-1)
        results_array.reverse()
        for arr in results_array:
            # check if the match is in the future, if it is, skip it
            # example arr: Wed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n          \nEmirates Cup
            result_date = arr.split("\n\n")[0].strip()
            result_date = datetime.strptime(result_date, "%a %b %d - %H:%M")
            if result_date.day >= current_date.day:
                continue
            match_obj = parse_result_array(arr)
            results += [match_obj]
            if len(results) >= number:
                return results
    return results


def find_fixtures(matches, number: int):
    """Takes the matches and returns the next number of fixtures"""
    fixtures = []
    for match in matches:
        # match.text is the text of the table, will need to parse this
        # '\n\n          August 2023\n            \n\n\nWed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n
        # \nEmirates Cup          \n\n\nSun Aug 6 - 16:00\n\n  Manchester City\n          \n 1 - 1\n\n  Arsenal\n
        # \nFA Community Shield          \n\n\nSat Aug 12 - 13:00\n\n  Arsenal\n          \n 2 - 1\n\n
        # Nottingham Forest\n          \nPremier League          \n\n\nMon Aug 21 - 20:00\n\n  Crystal Palace\n
        # \n 0 - 1\n\n  Arsenal\n          \nPremier League          \n\n\nSat Aug 26 - 15:00\n\n  Arsenal\n
        # \n 2 - 2\n\n  Fulham\n          \nPremier League          \n\n\n'
        # first text after \n\n is the month and year, if the month is before the current month, pop it out
        match_month = match.text.split("\n\n")[1].strip()
        match_month = datetime.strptime(match_month, "%B %Y")
        current_date = datetime.utcnow()
        if match_month.year <= current_date.year and match_month.month < current_date.month:
            continue
        # the rest can be split by \n\n\n
        match_array = match.text.split("\n\n\n")
        match_year = match_array[0].split("\n\n")[1].strip()
        # remove anything in the string that is not a number
        match_year = "".join(filter(str.isdigit, match_year))
        match_year = datetime.strptime(match_year, "%Y")
        match_array.pop(0)  # pops the first element which is the month and year
        match_array.pop(-1)  # pops the last element which is an empty string
        for arr in match_array:
            # check if the match is in the past, if it is, skip it
            # example arr: Wed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n          \nEmirates Cup
            if "(Date and time TBC)" in arr:
                arr = arr.replace(
                    "(Date and time TBC)          ", "\n"
                )  # women's fixtures and results have this for some reason, replacing it with newline
            if "Time TBC" in arr:
                arr = arr.replace(
                    "Time TBC          ", "15:00 \n"
                )  # some mens fixtures have this, replacing it with midnight until we get the time
            match_date = arr.split("\n\n")[0].strip()
            try:
                match_date = datetime.strptime(match_date, "%a %b %d - %H:%M")
            except ValueError:
                # if a time hasnt been set, we should just skip it for now
                continue
            # change match_date.year to match_year.year
            match_date = match_date.replace(year=match_year.year)
            # check if the match is in the past, if it is, skip it
            if match_date < current_date:
                continue
            match_obj = parse_match_array(arr)
            fixtures += [match_obj]
            if len(fixtures) >= number:
                return fixtures
    return fixtures


def parse_match_array(match_array):
    """converts the str of matches into a Match Object"""
    match_obj = Match("", "", "", "")
    # example match string:
    # 'Wed Nov 1 - 19:30\n\n  West Ham United\n          \n 3 - 1\n\n  Arsenal\n          \nCarabao Cup          '
    # split by \n\n
    match_str = match_array.split("\n\n")
    # first element is the date and time starting with the day of the week, month, date, time
    # second element is the home team
    # third element is the score
    # fourth element is the away team
    # fifth element is the competition
    match_obj.date = match_str[0].split(" - ")[0].strip()
    match_obj.time = match_str[0].split(" - ")[1].strip()
    match_str = match_str[1].split("\n")
    home_team = match_str[0].strip()
    away_team = match_str[4].strip()
    match_obj.comp = match_str[6].strip()
    match_obj.team = get_opponent(home_team, away_team)
    return match_obj


def parse_result_array(result_array):
    """converts the str of matches into a Result Object"""
    result_obj = Result("", "", "", "", "", "")
    result_str = result_array.split("\n\n")
    result_obj.date = result_str[0].split(" - ")[0].strip()
    result_obj.time = result_str[0].split(" - ")[1].strip()
    home_team = result_str[1].split("\n")[0].strip()
    score = result_str[1].split("\n")[2].strip()
    away_team = result_str[-1].split("\n")[0].strip()
    result_obj.comp = result_str[2].split("\n")[2].strip()
    result_obj.team = get_opponent(home_team, away_team)
    result_obj.score = score
    result_obj.wonOrLost = get_won_or_lost(home_team, score)
    return result_obj


def get_won_or_lost(home_team, score):
    """determines if Arsenal won or lost the match"""
    home_score = int(score.split(" - ")[0].strip())
    away_score = int(score.split(" - ")[1].strip())
    if home_team == "Arsenal":
        if home_score > away_score:
            return "W"
        elif home_score < away_score:
            return "L"
        else:
            return "D"
    else:
        if home_score > away_score:
            return "L"
        elif home_score < away_score:
            return "W"
        else:
            return "D"


def get_opponent(home_team, away_team):
    """returns the opponent of the match"""
    if home_team == "Arsenal":
        return f"{away_team} (H)"
    else:
        return f"{home_team} (A)"


def get_international_cup(league_code=50, end_date=20210711):
    """Gets the current international cup progression"""
    # originally written for the euros so i have set the euros parameters as default
    matches = []
    body = ""
    today = datetime.today().strftime("%Y%m%d")
    while len(matches) < 5 and int(today) < end_date:
        fixtures = fotmob.getLeague(league_code, "overview", "league", "UTC", today)
        for match in fixtures[:5]:
            matches.append(match)
            if len(matches) > 5:
                break
        today = str(int(today) + 1)
    for match in matches:
        body += match.getDate() + " | "
        if match.getKickOff():
            if match.getKickOff() == "In Progress":
                body += match.getResult() + " | "
            else:
                body += match.getKickOff() + " | "
        else:
            body += match.getResult() + " | "
        body += match.getHomeTeam() + " v " + match.getAwayTeam() + "\n"
    return body


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(FixturesCog(bot))
