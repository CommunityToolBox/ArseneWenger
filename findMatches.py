#!/usr/bin/python
# -*- coding: utf-8 -*-

import praw,re,logging,logging.handlers,requests,requests.auth,sys,json,unicodedata
from praw.models import Message
from collections import Counter
from itertools import groupby
from time import sleep
from bs4 import BeautifulSoup
from fotmob import fotmob
from datetime import datetime,timedelta
from datetime import date

i = 0

class Match(object):
    date = ""
    homeTeam = ""
    awayTeam = ""
    timeResult = ""
    comp = ""

    def __init__(self,date,homeTeam,awayTeam,timeResult,comp):
        self.date = date
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.timeResult = timeResult
        self.comp = comp

def getTimestamp():
        dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
        hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
        min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
        t = '[' + hr + ':' + min + '] '
        return dt + t

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

def parseFixtures():
    website = "https://www.arsenal.com/fixtures"
    fixturesWebsite = requests.get(website, timeout=15)
    fixture_html = fixturesWebsite.text
    soup = BeautifulSoup(fixture_html, "lxml")
    table = soup.find("div",{"class","accordions"})
    matches = table.findAll("article",attrs={'role':'article'})
    #fixtures[0] now holds the next match
    return matches

def parseResults():
    website = "https://www.arsenal.com/results"
    fixtureWebsite = requests.get(website,timeout=15)
    fixture_html = fixtureWebsite.text
    soup = BeautifulSoup(fixture_html, "lxml")
    table = soup.find("div",{"class","accordions"})
    matches = table.findAll("article",attrs={'role':'article'})
    return matches

def findFixtures(matches, number):
    body = ""
    match = matches[0].find("div",{"class","fixture-match"})
    date = matches[0].find("time").text
    time = date.split('-')[1].strip()
    date = date.split('-')[0][3:].strip()
    comp = matches[0].find("div",{"class","event-info__extra"}).text
    teams = match.findAll("div",{"class","fixture-match__team"})
    homeTeam = teams[0].find("div",{"class","team-crest__name-value"}).text
    awayTeam = teams[1].find("div",{"class","team-crest__name-value"}).text
    homeAway = getLocation(teams)
    if homeAway == 0:
        team = awayTeam + " (H)"
    else:
        team = homeTeam + " (A)"
    body += "| " + date + " | " + time + " | " + team +" | " +comp+" |\n"
    if number == 0 or number > 10:
        x = 3
    else:
        x = number
    if len(matches) < x:
        x = len(matches)
    for i in range(1,x):
        match = matches[i].find("div",{"class","card__content"})
        try:
            date = matches[i].find("time").text
            time = date.split('-')[1].strip()
            date = date.split('-')[0][3:].strip()
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        except:
            time = "TBD"
            date = matches[i].find("div",class_=False, id=False).text.split(' ')
            date = (date[0][:3] + " " + date[1]).split(',')[0]
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        team = match.find("span",{"class","team-crest__name-value"}).text
        location = match.find("div",{"class","location-icon"})['title']
        if location == "Home":
            team = team + " (H)"
        else:
            team = team+ " (A)"
        body += "| " + date + " | " + time + " | " + team + " | " +comp+" |\n"
    return body


def findResults(matches):
    body = ""
    for i in range(2,0,-1):
        result = ""
        try:
            match = matches[i].find("div",{"class","card__content"})
        except:
            if i == 0:
                return body
            break
        date = matches[i].find("time").text
        date = date.split('-')[0][3:].strip()
        comp = matches[i].find("div",{"class","event-info__extra"}).text
        team = match.find("span",{"class","team-crest__name-value"}).text
        location = match.find("div",{"class","location-icon"})['title']
        homeScore = match.findAll("span",{"class","scores__score"})[0].text
        awayScore = match.findAll("span",{"class","scores__score"})[1].text
        if homeScore > awayScore:
            if location == "Home":
                result += " W "
            elif location == "Neutral":
                if team == "Arsenal":
                    result += " L "
                else:
                    result += " W "
            else:
                result += " L "
        elif homeScore < awayScore:
            if location == "Home":
                result += " L "
            elif location == "Neutral":
                if team == "Arsenal":
                    result += " L "
                else:
                    result += " W "
            else:
                result += " W "
        else:
            result += " D "
        result += homeScore +" - "+awayScore
        if location == "Home":
            team = team + " (H)"
        else:
            team = team+ " (A)"
        body += "| " + date + " | " + result + " | " + team + " | " +comp+" |\n"
    result = ""
    date = matches[0].find("time").text
    date = date.split('-')[0][3:].strip()
    match = matches[0].find("div",{"class","fixture-match"})
    comp = matches[0].find("div",{"class","event-info__extra"}).text
    teams = match.findAll("div",{"class","fixture-match__team"})
    homeTeam = teams[0].find("div",{"class","team-crest__name-value"}).text
    awayTeam = teams[1].find("div",{"class","team-crest__name-value"}).text
    homeAway = getLocation(teams)
    homeScore = match.findAll("span",{"class","scores__score"})[0].text
    awayScore = match.findAll("span",{"class","scores__score"})[1].text
    if homeScore > awayScore:
        if homeAway == 0:
            result += " W "
        else:
            result += " L "
    elif homeScore < awayScore:
        if homeAway == 0:
            result += " L "
        else:
            result += " W "
    else:
        result += " D "
    result += homeScore +" - "+awayScore
    if homeAway == 0:
        team = awayTeam + " (H)"
    else:
        team = homeTeam + " (A)"
    body += "| " + date + " | " + result + " | " + team +" | " +comp+" |\n"
    return body

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

def discordFixtures(number = 3):
    fixtures = parseFixtures()
    body = findFixtures(fixtures, number)
    return body

def discordResults():
    fixtures = parseResults()
    body = findResults(fixtures)
    return body 

def nextFixture():
    """Returns how many days, hours, and minutes are left until the next fixture"""
    body = discordFixtures(1)
    splitBod = body.split("|")
    if (date.today()).month == 12 and "jan" in (splitBod[1]).lower():
        nextMatchDate = f"""{((splitBod[1]).strip())} {((date.today()).year)+1}  {(splitBod[2]).strip()}"""
    else:
        nextMatchDate = f"""{((splitBod[1]).strip())} {(date.today()).year}  {(splitBod[2]).strip()}"""

    opponentInfo = f"""{(splitBod[3]).strip()}"""
    
    dateObject = dateObject = datetime.strptime(nextMatchDate, '%b %d %Y %H:%M')
    if (bst_flag()):
        delta = dateObject - (datetime.utcnow() + timedelta(hours=1))
    else:
        delta = dateObject - datetime.utcnow()
    if delta.days > 0:
        response = f"Next match is {opponentInfo} in {delta.days} days, {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes"
    else:
        response = f"Next match is {opponentInfo} in {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes"
    return response
