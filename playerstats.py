#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from tabulate import tabulate


def getPlayerStats(club):
    top_scorer = dict()
    metrics_wanted = {"goals"}  # Can be expanded to other metrics like assists, minutes played etc
    page = requests.get('https://fbref.com/en/squads/18bb7c10')  # TODO: add a config file and store club->id mapping
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", page.text), 'lxml')
    all_tables = soup.findAll("tbody")
    stats_table = all_tables[0]
    rows_player = stats_table.find_all('tr')

    for each in rows_player:
        if (each.find('th', {"scope": "row"}) != None):
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
    df_topscorers.index = df_topscorers.index + 1
    table = tabulate(df_topscorers, tablefmt='plain', colalign=['left', 'left'], showindex=False)
    return table

def getAssists(comp='Premier League'):
    tableurl="https://fbref.com/en/squads/18bb7c10/2021-2022/all_comps/Arsenal-Stats-All-Competitions"

    # Get table and convert to Dataframe
    page = requests.get(tableurl)
    x1=requests.get(tableurl, stream=True)
    x2=""
    ind=False
    for lines in x1.iter_lines():
      lines_d=lines.decode('utf-8')
      if "div_stats_player_summary" in lines_d:
        ind=True
        
      if ind:  
        x2=x2+lines_d
        
      if "tfooter_stats_player_summary" in lines_d:
        break
    
    tableslist=pd.read_html(x2)[0]
    # End
    columnlist=list(tableslist.columns)
    sorted_table=tableslist.sort_values([(comp,'Ast')],ascending=False) #Table containing all stats and assists in desc order
    sub_table=sorted_table[[('Unnamed: 0_level_0','Player'),(comp,'Ast')]].to_numpy().tolist()[0:5] # List containing only top 5 assists in desc order
    tabulate.PRESERVE_WHITESPACE=False
    table=tabulate(sub_table,headers=['Player','Ast'],tablefmt='pretty',colalign=('right','left',))
    table='Assist Stats: '+comp+'\n'+table
    return table
    

def main(msgLower):
    if msgLower=='!goals':
            return getGoalsScored('Arsenal')
    if msgLower=='!assists':
            return getAssists()
    elif len(msgLower.split(" "))>1:
            param=msgLower.split(" ")
            if param[1].strip()=='pl':
                    return getAssists('Premier League')
            elif param[1].strip()=='all':
                    return getAssists('Combined')
            elif param[1].strip()=='fa':
                    return getAssists('FA Cup')
            elif param[1].strip()=='efl':
                    return getAssists('EFL Cup')  
              
      
