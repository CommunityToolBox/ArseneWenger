import discord
import os
import requests
from bs4 import BeautifulSoup
import lxml
client = discord.Client()
class gamecheck:
    def __init__(self, name):
        if name == "leicester":
            source = requests.get("https://www.11v11.com/teams/arsenal/tab/opposingTeams/opposition/Leicester%20City/")
        elif name == "manutd":
            source = requests.get("https://www.11v11.com/teams/arsenal/tab/opposingTeams/opposition/Manchester%20United/")
        elif name == "mancity":
            source = requests.get("https://www.11v11.com/teams/arsenal/tab/opposingTeams/opposition/Manchester%20City/")


        soup = BeautifulSoup(source.text, 'lxml')
        games = soup.find_all(class_="result-status")
        allgames = []

        for game in games:
            allgames.append(game.text)
        self.last5 = allgames[-5:]
        
oqr = gamecheck("leicester")
utd = gamecheck("manutd")
mcy = gamecheck("mancity")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!history leicester'):
        await message.channel.send("Our last 5 games with this club:")
        await message.channel.send(oqr.last5)
    elif message.content.startswith('!history manutd'):
        await message.channel.send("Our last 5 games with this club:")
        await message.channel.send(utd.last5)
    elif message.content.startswith('!history mancity'):
        await message.channel.send("Our last 5 games with this club:")
        await message.channel.send(mcy.last5)
client.run("token")
