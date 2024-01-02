#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog with useful commands around fixtures
"""
import discord
import requests, requests.auth
from bs4 import BeautifulSoup
from fotmob import fotmob
from datetime import datetime,timedelta
from datetime import date
from discord.ext import commands
from discord import app_commands
if __name__ != "__main__":
    from utils import clamp_int


class FixturesCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot


    async def generate_fixtures_embed(self, interaction: discord.Interaction, team_type: str, count: int = 3):
        count = clamp_int(count, 1, 10)
        fixtures = parse_arsenal(team_type)
        fixture_list = findFixtures(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        team_name = getTeamName(team_type)
        embed.set_author(
            name=f"Next {len(fixture_list)} {team_name} Fixtures",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        for fixture in fixture_list:
            embed.add_field(
                name=f"{fixture.team} - {fixture.comp}",
                value=f"{fixture.date} {fixture.time}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="fixtures",
        description="Display the next N fixtures, default 3, max 10."
    )
    async def fixtures(self, interaction: discord.Interaction, count: int = 3):
        #defer
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "", count)

    @app_commands.command(
        name="wfixtures",
        description="Display the next N fixtures for women's team, default 3, max 10."
    )
    async def wfixtures(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_fixtures_embed(interaction, "women", count)
    
    async def generate_next_embed(self, interaction: discord.Interaction, team_type: str):
        """generates the embed for the next and wnext commands"""
        fixtures = parse_arsenal(team_type)
        fixture = findFixtures(fixtures, 1)[0]
        if (date.today()).month == 12 and "jan" in fixture.date.lower():
            next_match_date = f"""{fixture.date} {date.today().year+1}  {fixture.time}"""
        else:
            next_match_date = f"""{fixture.date} {(date.today()).year}  {fixture.time}"""

        #next_match_date example: Wed Nov 29 2023 20:00
        date_object = datetime.strptime(next_match_date, '%a %b %d %Y %H:%M')
        if bst_flag():
            delta = date_object - (datetime.utcnow() + timedelta(hours=1))
        else:
            delta = date_object - datetime.utcnow()

        if delta.days > 0:
            response = f"Next match is {fixture.team} in {delta.days} days, {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes"
        elif delta.days == 0:
            response = f"Next match is {fixture.team} in {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes"
        else:
            channel = discord.utils.get(interaction.guild.text_channels, name="live-games")
            response = f"There is a match playing right now! head over to <#{channel.id}>"

        embed = discord.Embed(
            color=0x9C824A,
            description=response
        )

        team_name = getTeamName(team_type)
        embed.set_author(
            name=f"Next {team_name} Game",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="next",
        description="Display the time between now in utc and the next men's match."
    )
    async def next(self, interaction: discord.Interaction):
        """Returns how many days, hours, and minutes are left until the next fixture"""
        #defer the response so that we don't get an unknown interaction error if it takes longer than 3 seconds
        await interaction.response.defer()
        # now we can generate the embed
        await self.generate_next_embed(interaction, "")
    
    @app_commands.command(
        name="wnext",
        description="Display the time between now in utc and the next women's match."
    )
    async def wnext(self, interaction: discord.Interaction):
        """Returns how many days, hours, and minutes are left until the next women's fixture"""
        #defer the response so that we don't get an unknown interaction error if it takes longer than 3 seconds
        await interaction.response.defer()
        # now we can generate the embed
        await self.generate_next_embed(interaction, "women")
        
    async def generate_results_embed(self, interaction: discord.Interaction, team_type: str, count: int = 3):
        count = clamp_int(count, 1, 10)
        fixtures = parse_arsenal(team_type)
        result_list = findResults(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        embed.set_author(
            name=f"Last {len(result_list)} results",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        for result in result_list:
            #add green check mark if won, red x if lost, light gray circle if draw
            if result.wonOrLost == 'W':
                icon = '✅'
            elif result.wonOrLost == 'L':
                icon = '❌'
            else:
                icon = '⬜'

            embed.add_field(
                name=f"{icon} against {result.team} - {result.comp}",
                value=f"{result.date} {result.time} | {result.score} | ",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="results",
        description="Show Recent Men's Results"
    )
    async def results(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_results_embed(interaction, "", count)
    
    @app_commands.command(
        name="wresults",
        description="Show Recent Women's Results"
    )
    async def wresults(self, interaction: discord.Interaction, count: int = 3):
        await interaction.response.defer()
        await self.generate_results_embed(interaction, "women", count)

    @commands.command(
        name="euro",
        aliases=("euros", ),
        help="Show recent results"
    )
    async def euro(self, ctx):
        body = getInternationalCup()
        await ctx.send(f"```{body}```")

    @commands.command(
        name="copa",
        aliases=("copas", ),
        help="Show results"
    )
    async def copa(self, ctx):
        body = getInternationalCup(44, 20210710)
        await ctx.send(f"```{body}```")

    @commands.command(
        name="olympic",
        aliases=("olympics", ),
        help="Show results"
    )
    async def olympic(self, ctx):
        body = getInternationalCup(66, 20210810)
        body = 'Men:\n' + body
        await ctx.send(f"```{body}```")
        body = getInternationalCup(65, 20210810)
        body = 'Women:\n' + body
        await ctx.send(f"```{body}```")

i = 0


class Match:
    def __init__(self, date, time, team, comp):
        self.date = date
        self.time = time
        self.team = team
        self.comp = comp

class Result:
    def __init__(self, date, time, team, comp, score, wonOrLost):
        self.date = date
        self.time = time
        self.team = team
        self.comp = comp
        self.score = score
        self.wonOrLost = wonOrLost

def getTeamName(team_type: str):
    """returns the team name based on the team type"""
    team_name = "Women's" if team_type == "women" else "Men's"
    return team_name

def getLocation(line):
    homeTeam = line[0].text.strip()
    if 'Arsenal' in homeTeam:
        return 0
    else:
        return 1


def bst_flag():
    """returns true if we are in bst"""
    date_plus_7 = datetime.utcnow().date() + timedelta(days=7)
    #BST falls between the last Sunday of march and the last sunday of october.
    if (datetime.utcnow().date()).month > 3 and (datetime.utcnow().date()).month < 11:
        return True
    #to account for that last sunday, if I add seven to the last remaining dates in march and october, i could account for that
    elif ((datetime.utcnow().date()).month) == 3 and (date_plus_7.month > 3 and date_plus_7.month < 11):
        return True
    else:
        return False

def parse_arsenal(gender="men"):
    """Gets the current arsenal fixtures"""
    if gender == "women":
        url = "https://www.arsenal.com/results-and-fixtures-list?field_arsenal_team_target_id=5"
    else:
        url = "https://www.arsenal.com/results-and-fixtures-list?"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

    # Example Table Class:
    response = requests.get(url,timeout=15, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    table = soup.select_one('div[class*="results-fixure--slimline"]')
    #find all table class="cols-0"
    matches = table.findAll("table",attrs={'class': 'cols-0'})
    return matches

def findResults(matches, number: int = 3):
    """takes the matches and returns the previous number of results"""
    results = []
    #reverse matches so we're working backwards
    matches.reverse()
    for match in matches:
        matchMonth = match.text.split('\n\n')[1].strip()
        matchMonth = datetime.strptime(matchMonth, '%B %Y')
        currentDate = datetime.utcnow()
        if matchMonth.year > currentDate.year or currentDate.month < matchMonth.month:
            continue
        #elseif match falls in the same month, but still in the future, skip it
        elif matchMonth.year == currentDate.year and currentDate.month == matchMonth.month and currentDate.day < matchMonth.day:
            continue
        #the rest can be split by \n\n\n
        resultsArray = match.text.split('\n\n\n')
        resultsArray.pop(0)
        resultsArray.pop(-1)
        resultsArray.reverse()
        for arr in resultsArray:
            #check if the match is in the future, if it is, skip it
            #example arr: Wed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n          \nEmirates Cup    
            resultDate = arr.split('\n\n')[0].strip()
            resultDate = datetime.strptime(resultDate, '%a %b %d - %H:%M')
            twoHoursFromNow = currentDate + timedelta(hours=2)
            if resultDate.day >= currentDate.day:
                continue
            matchObj = parseResultArray(arr)
            results += [matchObj]
            if len(results) >= number:
                return results
    return results

def findFixtures(matches, number: int):
    """Takes the matches and returns the next number of fixtures"""
    fixtures = []
    for match in matches:
        #match.text is the text of the table, will need to parse this
        #'\n\n          August 2023\n            \n\n\nWed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n          \nEmirates Cup          \n\n\nSun Aug 6 - 16:00\n\n  Manchester City\n          \n 1 - 1\n\n  Arsenal\n          \nFA Community Shield          \n\n\nSat Aug 12 - 13:00\n\n  Arsenal\n          \n 2 - 1\n\n  Nottingham Forest\n          \nPremier League          \n\n\nMon Aug 21 - 20:00\n\n  Crystal Palace\n          \n 0 - 1\n\n  Arsenal\n          \nPremier League          \n\n\nSat Aug 26 - 15:00\n\n  Arsenal\n          \n 2 - 2\n\n  Fulham\n          \nPremier League          \n\n\n'
        #first text after \n\n is the month and year, if the month is before the current month, pop it out
        matchMonth = match.text.split('\n\n')[1].strip()
        matchMonth = datetime.strptime(matchMonth, '%B %Y')
        currentDate = datetime.utcnow()
        if matchMonth.year <= currentDate.year and matchMonth.month < currentDate.month:
            continue
        #the rest can be split by \n\n\n
        matchArray = match.text.split('\n\n\n')
        matchYear = matchArray[0].split('\n\n')[1].strip()
        #remove anything in the string that is not a number
        matchYear = ''.join(filter(str.isdigit, matchYear))
        matchYear = datetime.strptime(matchYear, '%Y')
        matchArray.pop(0) #pops the first element which is the month and year
        matchArray.pop(-1) #pops the last element which is an empty string
        for arr in matchArray:
            #check if the match is in the past, if it is, skip it
            #example arr: Wed Aug 2 - 18:00\n\n  Arsenal\n          \n 1 - 1\n\n  Monaco\n          \nEmirates Cup    
            if "(Date and time TBC)" in arr:
                arr = arr.replace("(Date and time TBC)          ", "\n") #women's fixtures and results have this for some reason, replacing it with newline
            if "Time TBC" in arr:
                arr = arr.replace("Time TBC          ", "15:00 \n") #some mens fixtures have this, replacing it with midnight until we get the time
            matchDate = arr.split('\n\n')[0].strip()
            try:
                matchDate = datetime.strptime(matchDate, '%a %b %d - %H:%M')
            except ValueError:
                #if a time hasnt been set, we should just skip it for now
                continue
            #change matchDate.year to matchYear.year
            matchDate = matchDate.replace(year=matchYear.year)
            #check if the match is in the past, if it is, skip it
            if matchDate < currentDate:
                continue
            matchObj = parseMatchArray(arr)
            fixtures += [matchObj]
            if len(fixtures) >= number:
                return fixtures
    return fixtures

def parseMatchArray(matchArray):
    """converts the str of matches into a Match Object"""
    matchObj = Match("","","","")
    #example match string:'Wed Nov 1 - 19:30\n\n  West Ham United\n          \n 3 - 1\n\n  Arsenal\n          \nCarabao Cup          '
    #split by \n\n
    matchStr = matchArray.split('\n\n')
    #first element is the date and time starting with the day of the week, month, date, time
    #second element is the home team
    #third element is the score
    #fourth element is the away team
    #fifth element is the competition
    matchObj.date = matchStr[0].split(' - ')[0].strip()
    matchObj.time = matchStr[0].split(' - ')[1].strip()
    matchStr = matchStr[1].split('\n')
    homeTeam = matchStr[0].strip()
    awayTeam = matchStr[4].strip()
    matchObj.comp = matchStr[6].strip()
    matchObj.team = getOpponent(homeTeam, awayTeam)
    return matchObj

def parseResultArray(resultArray):
    """converts the str of matches into a Result Object"""
    resultObj = Result("","","","","","")
    resultStr = resultArray.split('\n\n')
    resultObj.date = resultStr[0].split(' - ')[0].strip()
    resultObj.time = resultStr[0].split(' - ')[1].strip()
    homeTeam = resultStr[1].split('\n')[0].strip()
    score = resultStr[1].split('\n')[2].strip()
    awayTeam = resultStr[-1].split('\n')[0].strip()
    resultObj.comp = resultStr[2].split('\n')[2].strip()
    resultObj.team = getOpponent(homeTeam, awayTeam)
    resultObj.score = score
    resultObj.wonOrLost = getWonOrLost(homeTeam, awayTeam, score)
    return resultObj

def getWonOrLost(homeTeam, awayTeam, score):
    """determines if Arsenal won or lost the match"""
    homeScore = int(score.split(' - ')[0].strip())
    awayScore = int(score.split(' - ')[1].strip())
    if homeTeam == 'Arsenal':
        if homeScore > awayScore:
            return 'W'
        elif homeScore < awayScore:
            return 'L'
        else:
            return 'D'
    else:
        if homeScore > awayScore:
            return 'L'
        elif homeScore < awayScore:
            return 'W'
        else:
            return 'D'
        


    
def getOpponent(homeTeam, awayTeam):
    """returns the opponent of the match"""
    if homeTeam == 'Arsenal':
        return f"{awayTeam} (H)"
    else:
        return f"{homeTeam} (A)"




def getInternationalCup(leagueCode = 50, endDate = 20210711): #originally written for the euros so i have set the euros parameters as default
    """Gets the current international cup progression"""
    matches = []
    body = ""
    today = datetime.today().strftime('%Y%m%d')
    while len(matches) < 5 and int(today) < endDate:
        fixtures = fotmob.getLeague(leagueCode,"overview","league","UTC",today)
        for match in fixtures[:5]:
            matches.append(match)
            if len(matches) > 5:
                break
        today = str(int(today) + 1)
    for match in matches:
        body += match.getDate() + " | "
        if match.getKickOff():
            if match.getKickOff() == 'In Progress':
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
