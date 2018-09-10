#!/usr/bin/python
# -*- coding: utf-8 -*-


import re,logging,logging.handlers,datetime,requests,requests.auth,sys,json,unicodedata
from praw.models import Message
from collections import Counter
from itertools import groupby
from time import sleep

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
        body += "|"+position+"|"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    else:
        for x in range(index, i):
            team = re.findall('a href=".*">(.*)<\/a>',table[x])[0]
            position = re.findall('<td class="pos">(.*)</td>',table[x])[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>',table[x])[0]
            points = re.findall('<td class="pts">(.*)</td>',table[x])[0]
            body += "|"+position+"|"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
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
            body += "|"+position+"|"+team+"|"+getSign(goalDiff)+"|"+points+"|\n"
    return body

def findArsenal(table):
    for index,pos in enumerate(table):
        team = re.findall('a href=".*">(.*)<\/a>',pos)[0]
        if team == "Arsenal":
            i = index
            position = re.findall('<td class="pos">(.*)</td>',pos)[0]
            goalDiff = re.findall('<td class="gd">(.*)</td>',pos)[0]
            points = re.findall('<td class="pts">(.*)</td>',pos)[0]
            body = "|"+position+"|"+team.upper()+"|"+getSign(goalDiff)+"|"+points+"|\n"
    topRange = i + 2
    botRange = i - 2
    if botRange <= 1:
        topRange += 1
    above = discordAbove(table, botRange, i)
    below = discordBelow(table, topRange, i)
    body = above + body + below
    return body


def parseWebsite():
    website = "http://www.espnfc.us/english-premier-league/23/table"
    tableWebsite = requests.get(website, timeout=15)
    table_html = tableWebsite.text
    fullTable = table_html.split('<div class="responsive-table">')[1]
    table = fullTable.split('<tr style="background-color:')
    #fixtures[0] now holds the next match
    return table

def discordMain():
    table = parseWebsite()
    body = findArsenal(table)
    return body
