#!/usr/bin/python
# -*- coding: utf-8 -*-

import praw,re,logging,logging.handlers,datetime,requests,requests.auth,sys,json,unicodedata
from praw.models import Message
from collections import Counter
from itertools import groupby
from time import sleep

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
    homeTeam = line[0]
    if homeTeam == 'Arsenal':
        return 0
    else:
        return 1



def parseWebsite():
    website = "https://www.arsenal.com/fixtures"
    fixturesWebsite = requests.get(website, timeout=15)
    fixture_html = fixturesWebsite.text
    soup = BeautifulSoup(fixture_html, "lxml")
    nextMatch = soup.find("div",{"class","accordions"})
    matches = table.findAll("article",attrs={'role':'article'})
    #fixtures[0] now holds the next match
    return matches



def discordNext(table, nextMatch):
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
    body += "| " + date + " | [](#icon-clock) " + time + " | []" + team +" | []" +getComp(comp)
    for i in range(1,3):
        match = matches[i].find("div",{"class","card__content"})
        try:
            date = matches[i].find("time").text
            time = date.split('-')[1].strip()
            date = date.split('-')[0][3:].strip()
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        except:
            time = "TBD"
            date = matches[i].find("div",class_=False, id=False).text[3:].strip()
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        team = match.find("span",{"class","team-crest__name-value"}).text
        location = match.find("div",{"class","location-icon"})['title']
        if location == "Home":
            team = team + " (H)"
        else:
            team = team+ " (A)"
        body += "| " + date + " | " + time + " | " + team + " | " +comp
    return body


def discordBefore(fixtures, nextMatch):
    body = ""
    for i in range(2,0,-1):
        result = ""
        match = matches[i].find("div",{"class","card__content"})
        date = matches[i].find("time").text
        date = date.split('-')[0][3:].strip()
        comp = matches[i].find("div",{"class","event-info__extra"}).text
        team = match.find("span",{"class","team-crest__name-value"}).text
        location = match.find("div",{"class","location-icon"})['title']
        homeScore = match.findAll("span",{"class","scores__score"})[0].text
        awayScore = match.findAll("span",{"class","scores__score"})[1].text
        if homeScore > awayScore:
            if location == "Home":
                result += " Win"
            else:
                result += " Loss"
        elif homeScore < awayScore:
            if location == "Home":
                result += " Loss"
            else:
                result += " Win"
        else:
            result += " Draw"
        result += homeScore +" - "+awayScore
        if location == "Home":
            team = team + " (H)"
        else:
            team = team + " (A)"
        body += "| " + date + " | " + result + " | " + team + " | " +getComp(comp)+"|\n"
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
            result += " Win "
        else:
            result += " Loss "
    elif homeScore < awayScore:
        if homeAway == 0:
            result += " Loss "
        else:
            result += " Win "
    else:
        result += " Draw "
    result += homeScore +" - "+awayScore
    if homeAway == 0:
        team = awayTeam + " (H)"
    else:
        team = homeTeam + " (A)"
    body += "| " + date + " | " + result + " | " + team +" | " +getComp(comp)+"|\n"

    body +="|||\n"
    return body


def discordMatches(fixtures, index):
    body = ""
    team = ""
    x = index + 3
    for s in range(index, x):
        date = re.findall('div class="date">(.*)<\/div>',fixtures[s])[0]
        date = date.split(',')[0]
        time = re.findall('<div class="time gmt-time" data-time="(.*)">',fixtures[s])[0]
        time = re.findall('.*T(.*):',time)[0]
        comp = re.findall('<div class="league">(.*)<\/div>',fixtures[s])[0]
        teams = re.findall('<div class="team-name.*">(.*)<\/div>',fixtures[s])
        homeTeam = teams[0]
        awayTeam = teams[1]
        homeAway = getLocation(teams)
        if homeAway == 0:
            team = awayTeam + " (H)"
        else:
            team = homeTeam + " (A)"
        body += "| " + date + " |  " + time + " | " + team +" | " +comp+" |\n"
    return body

def discordResults(fixtures,index):
    body = ""
    team = ""
    x = index - 3
    for s in range(x, index): 
        result = ""
        date = fixtures[s].find("div",{"class","date"}).text
        date = date.split(',')[0]
        comp = fixtures[s].find("div",{"class","league"}).text
        teams = fixtures[s].findAll("div",{"class","team-name"})
        homeTeam = teams[0].text
        awayTeam = teams[1].text
        if fixtures[s].find("div",{"class","status"}).text == "FT-Pens":
            homeScore = fixtures[s].find("span",{"class",re.compile(r'home-score score-value')})[0].text
            homePenScore = re.findall('\(([0-9])\)',homeScore)[0]
            homeScore = re.findall('\s+([0-9])',homeScore)[0]
            awayScore = fixtures[s].findAll("span",{"class",re.compile(r'away-score score-value')})[0].text
            awayPenScore = re.findall('\(([0-9])\)',awayScore)[0]
            awayScore = re.findall('([0-9])\s+',awayScore)[0]
            homeAway = getLocation(teams)
            #0 for home, 1 for away
            if homePenScore > awayPenScore:
                if homeAway == 0:
                    result += "win) "
                else:
                    result += "loss) "
            elif homePenScore < awayPenScore: 
                if homeAway == 0:
                    result += "loss) "
                else:
                    result += "win) "
            result += homeScore + " ("+homePenScore+") - ("+awayPenScore+") "+awayScore
            if homeAway == 0:
                team = awayTeam + " (H)"
            else:
                team = homeTeam + " (A)"
        else:
            homeScore = fixtures[s].findAll("span",{"class",re.compile(r'home-score score-value')})[0].text
            awayScore = fixtures[s].findAll("span",{"class",re.compile(r'away-score score-value')})[0].text
            homeAway = getLocation(teams)
            #0 for home, 1 for away
            homeAway = getLocation(teams)
            if homeScore > awayScore:
                if homeAway == 0:
                    result += "win "
                else:
                    result += "loss "
            elif homeScore < awayScore: 
                if homeAway == 0:
                    result += "loss "
                else:
                    result += "win "
            else:
                result += "draw "
            result += homeScore +" - "+awayScore
            if homeAway == 0:
                team = awayTeam + " (H)"
            else:
                team = homeTeam + " (A)"
        body += "| " + date + " | " + result + " | " + team +" | " +comp+" |\n"
    return body


def parseNext(nextFixture):
    date = nextFixture.find("div",{"class","date"}).text
    time = re.search('.*T(.*)\.',nextFixture.find("div",{"class","time"})['data-time']).group(1)
    comp = nextFixture.find("div",{"class","league"}).text
    teams = nextFixture.findAll("div",{"class","team-name"})
    homeTeam = teams[0]
    awayTeam = teams[1]
    nextMatch = Match(date,homeTeam,awayTeam,time,comp)
    return nextMatch

def discordFixtures():
    fixtures = parseWebsite()
    #nextMatch = parseNext(nextMatch)   
    body = discordNext(fixtures,nextMatch)
    return body 

def discordResult():
    fixtures = parseWebsite()
    #nextMatch = parseNext(nextMatch)   
    body = discordBefore(fixtures,nextMatch)
    return body 
