#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from tabulate import tabulate


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
    table=tabulate(df_topscorers,tablefmt='plain',colalign=['left','left'],showindex=False)
    return table

def main(msgLower):
    match msgLower:
      case '!goals':
          return getGoalsScored('Arsenal')
