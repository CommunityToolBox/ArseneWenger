"""
A cog with useful commands around fixtures
"""

import datetime
import logging
import re
from typing import Literal

import discord
import requests
import requests.auth
from bs4 import BeautifulSoup, ResultSet, Tag
from discord import app_commands
from discord.ext import commands
from fotmob import fotmob
from pydantic import BaseModel

if __name__ != "__main__":
    from utils import clamp_int, make_discord_timestamp

logger = logging.getLogger(__name__)


class Fixture(BaseModel):
    date: datetime.datetime
    opponent: str
    location: Literal["Home", "Away"]
    competition: str
    scoreline: str = ""
    result: Literal["W", "L", "D"] | None = None


class FixturesCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    async def generate_fixtures_embed(
        self, interaction: discord.Interaction, team_type: str, count: int = 3
    ):
        """Create an embed for the requested team and number of fixtures

        Args:
            interaction: The received discord message
            team_type: men or women's team
            count: number of fixtures to use
        """
        count = clamp_int(count, 1, 20)
        fixtures = parse_arsenal(team_type)
        fixture_list = find_fixtures(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        team_name = getTeamName(team_type)
        embed.set_author(
            name=f"Next {len(fixture_list)} {team_name} Fixtures",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png",
        )

        for fixture in fixture_list:
            discord_aware_stamp = make_discord_timestamp(fixture.date)
            embed.add_field(
                name=f"{fixture.opponent} - {fixture.competition}",
                value=f"{discord_aware_stamp}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="fixtures", description="Display the next N fixtures, default 3, max 10."
    )
    async def fixtures(self, interaction: discord.Interaction, count: int = 3):
        # defer
        logger.info("Received /fixtures request")
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "", count)

    @app_commands.command(
        name="wfixtures",
        description="Display the next N fixtures for women's team, default 3, max 10.",
    )
    async def wfixtures(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "women", count)

    async def generate_next_embed(
        self, interaction: discord.Interaction, team_type: str
    ):
        """generates the embed for the next and wnext commands"""
        fixtures = parse_arsenal(team_type)
        fixture = find_fixtures(fixtures, 1)[0]
        date = datetime.datetime.now(tz=datetime.UTC)

        delta = fixture.date - date
        discord_timestamp = make_discord_timestamp(fixture.date)
        if delta.days > 0:
            response = f"Next match is {fixture.opponent} in {delta.days} days, {delta.seconds // 3600} hours, {(delta.seconds // 60) % 60} minutes on {discord_timestamp}"
        elif delta.days == 0:
            response = f"Next match is {fixture.opponent} in {delta.seconds // 3600} hours, {(delta.seconds // 60) % 60} minutes on {discord_timestamp}"
        else:
            channel = discord.utils.get(
                interaction.guild.text_channels, name="live-games"
            )
            response = (
                f"There is a match playing right now! head over to <#{channel.id}>"
            )

        embed = discord.Embed(color=0x9C824A, description=response)

        team_name = getTeamName(team_type)
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

    async def generate_results_embed(
        self, interaction: discord.Interaction, team_type: str, count: int = 3
    ):
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
            if result.result == "W":
                icon = "✅"
            elif result.result == "L":
                icon = "❌"
            else:
                icon = "⬜"

            embed.add_field(
                name=f"{icon} against {result.opponent} - {result.competition}",
                value=f"{result.date} | {result.scoreline} | ",
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
        body = getInternationalCup()
        await ctx.send(f"```{body}```")

    @commands.command(name="copa", aliases=("copas",), help="Show results")
    async def copa(self, ctx):
        body = getInternationalCup(44, 20210710)
        await ctx.send(f"```{body}```")

    @commands.command(name="olympic", aliases=("olympics",), help="Show results")
    async def olympic(self, ctx):
        body = getInternationalCup(66, 20210810)
        body = "Men:\n" + body
        await ctx.send(f"```{body}```")
        body = getInternationalCup(65, 20210810)
        body = "Women:\n" + body
        await ctx.send(f"```{body}```")


i = 0


def getTeamName(team_type: str):
    """returns the team name based on the team type"""
    team_name = "Women's" if team_type == "women" else "Men's"
    return team_name


def parse_arsenal(gender="men") -> ResultSet[Tag]:
    """Gets the current arsenal fixtures

    Returns:
        A BeautifulSoup ResultSet containing all matches for the season.
    """
    if gender == "women":
        url = "https://www.arsenal.com/results-and-fixtures-list?field_arsenal_team_target_id=5"
    else:
        url = "https://www.arsenal.com/fixtures/men/printable/20262027"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    }

    # Example Table Class:
    response = requests.get(url, timeout=15, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    matches = soup.find_all(
        "div", class_=re.compile("printable_printable_hero_box__.*")
    )
    return matches


def parse_result(match: Tag) -> str:
    """Grabs the scoreline from a match

    Args:
        match: bs4 tag of a match
    Returns:
        A basic scoreline matching x - x format
    """
    result = match.find(
        "div", class_=re.compile("printable_printable_hero_box_details__.*")
    )
    if not result:
        raise ValueError(f"Unable to parse scoreline from match '{match}'")
    scores = result.find(
        "div", class_=re.compile("printable_printable_hero_box_details_result__.*")
    )
    if scores:
        return scores.text


def find_results(matches: ResultSet[Tag], number: int = 3) -> list[Fixture]:
    """Takes the matches and returns the previous number of results

    Args:
        matches: A ResultSet containing the html of the fixtures table
        number: Number of previous results to return

    Returns:
        A list of previous results
    """
    next_match_int = find_next_match(matches)
    if next_match_int != -1:
        # Remove all fixtures we haven't played yet
        matches = ResultSet(source=None, result=matches[:next_match_int])
    results = []
    # reverse matches so we're working backwards
    matches.reverse()
    for match in matches:
        date = parse_date(match)
        (opponent, location) = parse_opponent(match)
        competition_parsed = match.find(
            "div", class_=re.compile("printable_printable_hero_box_type__.*")
        )
        if competition_parsed:
            competition = competition_parsed.text
        scoreline = parse_result(match)
        result = get_won_or_lost(scoreline, location)
        results += [
            Fixture(
                date=date,
                opponent=opponent,
                location=location,
                competition=competition,
                scoreline=scoreline,
                result=result,
            )
        ]
        if len(results) >= number:
            return results
    return results


def clean_date_string(date_str: str) -> str:
    """Cleans up months abbreviated in ways we don't expect

    Args:
        String representing a date following the Weekday Month Day - HH:MM format

    Returns:
        The same string but with properly abbreviated month.
    """
    # Stupid UK abbreviations
    month_map = {"sept": "Sep"}

    def replace_month(match):
        word = match.group(0)
        return month_map.get(word.lower(), word)

    return re.sub(r"[A-Za-z]+", replace_month, date_str)


def parse_date(match):
    """Return a datetime for the given match

    Args:
        match: A specific match from the Resultset
    Returns:
        Datetimeobject of the match date
    """
    date_string = match.find(
        "div", class_=re.compile("printable_printable_hero_box_date.*")
    ).text
    date_string = clean_date_string(date_string)
    parsed = datetime.datetime.strptime(date_string, "%a %b %d - %H:%M").replace(
        tzinfo=datetime.UTC
    )
    current_year = datetime.datetime.now(tz=datetime.UTC).year
    target_year = current_year if parsed.month >= 7 else current_year + 1
    date = parsed.replace(year=target_year)
    return date


def parse_opponent(match: Tag) -> tuple:
    """Find the opponent and match location

    Args:
        match: Bs4 Tag containing match participants

    Returns:
        a tuple containing the opponent name and if the match is Home or Away
    """
    details = match.find("div", class_="printable_printable_hero_box_details__JTszY")
    if not details:
        raise ValueError(f"Unable to parse teams for fixture: {match}")
    home = details.find(
        "div", class_=re.compile("printable_printable_hero_box_details_comp1.*")
    )
    away = details.find(
        "div", class_=re.compile("printable_printable_hero_box_details_comp2.*")
    )
    if home:
        home = home.text
    if away:
        away = away.text
    if home == "Arsenal":
        return (away, "Home")
    else:
        return (home, "Away")


def find_next_match(matches: ResultSet) -> int:
    """Return the index of the last match without a result

    Args:
        matches: ResultSet containing all matches of the season

    Returns:
        The index in matches for the next fixture to be played
    """
    today = datetime.datetime.now(tz=datetime.UTC)
    for i, match in enumerate(matches):
        date = parse_date(match)
        if date >= today:
            return i
    # If we get here then the season is over and there are no more fixtures
    return -1


def find_fixtures(matches: ResultSet[Tag], number: int) -> list[Fixture]:
    """Takes the matches and returns the next number of fixtures

    Args:
        matches: A ResultSet containing the html of the table
        number: Number of next fixtures to return

    Returns:
        A list of upcoming fixtures

    """
    # matches contains all matches of the season so we should skip all the matches we've played
    next_match_int = find_next_match(matches)
    if next_match_int == -1:
        return []
    fixtures = []
    for match in matches[next_match_int:]:
        date = parse_date(match)
        (opponent, location) = parse_opponent(match)
        competition_parsed = match.find(
            "div", class_="printable_printable_hero_box_type__JkjSv"
        )
        if competition_parsed:
            competition = competition_parsed.text
        fixtures += [
            Fixture(
                date=date, opponent=opponent, location=location, competition=competition
            )
        ]
        if len(fixtures) >= number:
            return fixtures
    return fixtures


def get_won_or_lost(scoreline, location):
    """Determine if Arsenal won, lost or drew the result"""
    home_score, away_score = map(int, scoreline.split(" - "))
    if location == "Home":
        if home_score > away_score:
            return "W"
        elif home_score < away_score:
            return "L"
    else:
        if home_score > away_score:
            return "L"
        elif home_score < away_score:
            return "W"
    return "D"


def getInternationalCup(
    leagueCode=50, endDate=20210711
):  # originally written for the euros so i have set the euros parameters as default
    """Gets the current international cup progression"""
    matches = []
    body = ""
    today = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d")
    while len(matches) < 5 and int(today) < endDate:
        fixtures = fotmob.getLeague(leagueCode, "overview", "league", "UTC", today)
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


def main():
    fixtures = parse_arsenal()
    find_fixtures(fixtures, 10)


if __name__ == "__main__":
    main()
