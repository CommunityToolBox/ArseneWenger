#!/usr/bin/python
# -*- coding: utf-8 -*-


import re,logging,logging.handlers,datetime,requests,requests.auth,sys,json,unicodedata
from praw.models import Message
from collections import Counter
from itertools import groupby
from time import sleep
from bs4 import BeautifulSoup
import tabulate

def getTimestamp():
        dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
        hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
        min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
        t = '[' + hr + ':' + min + '] '
        return dt + t
 

def getSign(goalDiff):
    if int(goalDiff) > 0:
        return "+"+goalDiff
    return goalDiff

def discordAbove(table, index, i):
    body = ""
    if index < 0:
        return body
    elif index == 0:
        team = re.findall('a href=".*">(.*)<\/a>',table[1])[0]
        position = re.findall('<td class="pos">(.*)</td>',table[1])[0]
        goalDiff = re.findall('<td class="gd">(.*)</td>',table[1])[0]
        points = re.findall('<td class="pts">(.*)</td>',table[1])[0]
        body += "| "+position+" |"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    else:
        for x in range(index, i):
            team = re.findall('a href=".*">(.*)<\/a>',table[x])[0]
            position = re.findall('<td class="pos">(.*)</td>',table[x])[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>',table[x])[0]
            points = re.findall('<td class="pts">(.*)</td>',table[x])[0]
            body += "| "+position+" |"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    return body
        

def discordBelow(table, index,i):
    body = ""
    if index < 5:
        index = 5
    for x in range(i+1, index+1):
            team = re.findall('a href=".*">(.*)<\/a>',table[x])[0]
            position = re.findall('<td class="pos">(.*)</td>',table[x])[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>',table[x])[0]
            points = re.findall('<td class="pts">(.*)</td>',table[x])[0]
            body += "| "+position+" |"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    return body

def findArsenal(table):
    header = "| Pos |  Team  | GD | Pts |\n"
    for index,pos in enumerate(table):
        team = re.findall('a href=".*">(.*)<\/a>',pos)[0]
        if team == "Arsenal":
            i = index
            position = re.findall('<td class="pos">(.*)</td>',pos)[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>',pos)[0]
            points = re.findall('<td class="pts">(.*)</td>',pos)[0]
            body = "| "+position+" |"+team.upper()+"|"+getSign(goalDiff)+"|"+points+"|\n"
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
    #fixtures[0] now holds the next match
    return table

def shortenedClubNames(club):
  clublist={
    "Chelsea":"Chelsea",
    "Manchester City":"Man City",
    "Brighton and Hove Albion":"Brighton",
    "Tottenham Hotspur":"Spurs",
    "Manchester United": "Man Utd",
    "West Ham United": "West Ham",
    "Everton":"Everton",
    "Wolverhampton Wanderers":"Wolves",
    "Leicester City":"Leicester",
    "Arsenal":"Arsenal",
    "Aston Villa": "Villa",
    "Crystal Palace":"Palace",
    "Southampton":"Southampton",
    "Watford":"Watford",
    "Leeds United":"Leeds",
    "Burnley":"Burnley",
    "Newcastle United":"Newcastle",
    "Norwich City":"Norwich",
    "Brentford":"Brentford",
    "Liverpool":"L'pool"
  }
  return clublist[club]

def discordMain():
    tableurl="https://www.skysports.com/premier-league-table"
    page= requests.get(tableurl, timeout=15).text
    pagesoup = BeautifulSoup(page, 'html.parser')
    tablemain=pagesoup.find('table',{'class':'standing-table__table'})

    headers=tablemain.find('thead')
    data=[]
    
    #Gets table headers
    cols = headers.find_all('th')
    cols = [ele.text.strip() for ele in cols]
    cols.pop()
    cols.pop(6)
    cols.pop(6)
    data.append([ele for ele in cols if ele]) # Get rid of empty values

    #Gets table body
    tablebody=tablemain.find('tbody')
    rows = tablebody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols[1]=shortenedClubNames(cols[1])
        cols.pop(6)
        cols.pop(6)
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    for row in data:
      if row[1]=='Arsenal':
        row[0]="‣ "+row[0]
        # row.insert(0,"►")
        # row.append("◄")
      

    table=tabulate.tabulate(data,headers='firstrow',tablefmt='simple',colalign=('right',))
    print(table)
    return table #Returns table
