#!/usr/bin/python
# -*- coding: utf-8 -*-


import praw,re,logging,logging.handlers,datetime,requests,requests.auth,sys,json,unicodedata
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
