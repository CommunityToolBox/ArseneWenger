#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from bs4 import BeautifulSoup
import csv,sys,getopt
import requests
from time import sleep
import json, re

CONF = {
    "url": "https://fbref.com/en/",
    "leagues": {
        "la_liga": "comps/12/L-Liga-Stats",
        "english_premier_league": "comps/9/Premier-League-Stats",
        "bundesliga": "comps/20/Bundesliga-Stats",
        "ligue_1": "comps/13/Ligue-1-Stats",
        "serie_a": "comps/11/Serie-A-Stats",
        "eredivisie": "comps/23/Dutch-Eredivisie-Stats",
        "russian_premier_league": "comps/30/Russian-Premier-League-Stats",
        "english_championship": "comps/10/Championship-Stats",
    },
}



def getPlayerStats(club):
    top_scorer = dict()
    metrics_wanted = {"goals"} #Can be expanded to other metrics like assists, minutes played etc
    page = requests.get('https://fbref.com/en/squads/18bb7c10') #TODO: add a config file and store club->id mapping
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", page.text), 'lxml')
    all_tables = soup.findAll("tbody")
    stats_table = all_tables[0]
    rows_player = stats_table.find_all('tr')

    for each in rows_player:
        if(each.find('th',{"scope":"row"}) != None):
            name = each.find('th', {"data-stat": "player"}).text.strip().encode().decode("utf-8")
            if 'player' in top_scorer:
                top_scorer['player'].append(name)
            else:
                top_scorer['player'] = [name]
            for f in metrics_wanted:
                cell = each.find("td", {"data-stat": f})
                a = cell.text.strip().encode()
                text = a.decode("utf-8")
                if f in top_scorer:
                    top_scorer[f].append(text)
                else:
                    top_scorer[f] = [text]
    df_topscorers = pd.DataFrame.from_dict(top_scorer)
    return df_topscorers

def getGoalsScored(club):
    df_topscorers = getPlayerStats(club).sort_values(by=['goals'], ascending=False, ignore_index=True).head(5)
    df_topscorers.index = df_topscorers.index+1
    return df_topscorers

def main(msgLower):
    match msgLower:
        case '!goals':
            return getGoalsScored('Arsenal')