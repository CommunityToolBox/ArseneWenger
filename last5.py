import discord
import os
import requests
from bs4 import BeautifulSoup
import lxml
client = discord.Client()
bob =123
class GameCheck:
    def __init__(self, name):
            source = requests.get(f"https://www.11v11.com/teams/arsenal/tab/opposingTeams/opposition/{name}")
            soup = BeautifulSoup(source.text, 'lxml')
            games = soup.find_all(class_="result-status")
            allgames = []

            for game in games:
                allgames.append(game.text)
            self.last5 = allgames[-5:]
      
oqr = GameCheck("Leicester City/")
utd = GameCheck("Manchester United/")
mcy = GameCheck("Manchester City/")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!history leicester'):
        await message.channel.send(f"`Our last 5 games with this club: {oqr.last5}`")
    elif message.content.startswith('!history manutd'):
        await message.channel.send(f"`Our last 5 games with this club: {utd.last5}`")
    elif message.content.startswith('!history mancity'):
       await message.channel.send(f"`Our last 5 games with this club: {mcy.last5}`")
client.run("token")
