import discord
import datetime,sys,re
import random
from random import randint
import findMatches
import getTable
import europaTable
#import schedule
from time import sleep
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont

prefix = '!'
bot = discord.Client()


def getTimestamp():
    dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
    hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
    min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
    t = '[' + hr + ':' + min + '] '
    return dt + t

def fetchRandomFact(manager):
    if manager == 'wenger':
        return wengerFact()
    if manager == 'unai':
        return unaiFact()
    if manager == 'arteta':
        return artetaFact()
    else:
        return "Sorry, that manager doesn't exist."
def wengerFact():
    try:
        facts = 'wengerFacts.txt'
        with open(facts,'r') as f:
            content = f.readlines()
        fact = random.choice(content)
        return fact
        #return random.choice(content)
    except:    
        print(getTimestamp()+"errors reading facts file")

def unaiFact():
    try:
        facts = 'unaiFacts.txt'
        with open(facts,'r') as f:
            content = f.readlines()
        fact = random.choice(content)
        return fact
        #return random.choice(content)
    except:    
        print(getTimestamp()+"errors reading facts file")

def artetaFact():
    try:
        facts = 'artetaFacts.txt'
        with open(facts,'r') as f:
            content = f.readlines()
        fact = random.choice(content)
        return fact
        #return random.choice(content)
    except:    
        print(getTimestamp()+"errors reading facts file")

def helpMessage():
    help = '```\n'
    help += prefix+'help\nDisplay this message.\n'
    help += prefix+'table\nDisplay the current Premier League Table.\n'
    help += prefix+'europa\nDisplay the Europa League table.\n'
    help += prefix+'wengerfact\nGet a random fact about our lord and savior Arsene Wenger.\n'
    help += prefix+'unaifact\nGet a random fact about our former manager Unai Emery.\n'
    help += prefix+'artetafact\nGet a random fact about our manager Unai Emery.\n'
    help += prefix+'fixtures\nDisplay the next 3 fixtures.\n'
    help += prefix+'fixtures #\nDisplay the next # fixtures. Max 10.\n'
    help += prefix+'next\nDisplay the time between now in utc and the next match.\n'
    help += prefix+'wengyboi <#>\nMake a wengyboi of # length! Max 10.\n'
    help += '```'
    return help

def makeWenger(message):
    message = message.split(' ')[1]
    if int(message) > 10:
        message = 10
    body = '<:ArseneTop:522209469547937802>\n'
    for i in range(0,int(message)):
        body += '<:ArseneMid:522209585403265045>\n'
    body += '<:ArseneBot:522209598464196608>\n'
    return body

def bannedThings():
    with open('banned.txt', 'r') as f:
        banned = f.read().splitlines()
    return banned

def clearMessage(message):
    return 

def copyPasta():
    num = randint(0,1)
    body = ""
    if num == 0:
        body = 'Right now I\'m sitting outside of the Tony Adams Statue and I am still as <:moh:358216187752087552> passionate <:moh:358216187752087552> about this club as I was the first time my uncle <:ArseneTop:346679833020989440>  took me to a game in 1991. I\'m reading the engravings on the paving outside the stadium and it fills me with <:tr7:239057992928985089>  pride. Through the ups  <:ozgasm:332570750290755586> and the downs <:wut:344131531108909056> we are fucking<:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> . No matter what \"faction\" <:thethinker:337164686849998849> you may fall under we are Arsenal. If you are more concerned with <:kappa:339386429392027648> WengerOut memes or <:gaffer:344131531096457216> AKB and arguing on the internet then go find another team to support. <:laca:341950939055259650> <:laca:341950939055259650> I\'m reading the testimony of generations of people who supported this club wholeheartedly <:thierry:344131530676764682>, through good and bad. <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> We are Arsenal. <:Arsenal:239341895845675008> <:Arsenal:239341895845675008> Never forget that <:gaffer:344131531096457216>'
    if num == 1:
        body = "To be fair, you have to have a very high IQ to understand Arsenal football. The tactics are extremely subtle, and without a solid grasp of the 3-4-2-1 formation most of the crosses will go over a typical striker’s head. There’s also Wenger’s nihilistic outlook, which is deftly woven into his lineup- his personal philosophy draws heavily from Herbert Chapman literature, for instance. The fans understand this stuff; they have the intellectual capacity to truly appreciate the depths of these losses, to realise that they’re not just funny- they say something deep about LIFE. As a consequence people who dislike the Arsenal truly ARE idiots- of course they wouldn’t appreciate, for instance, the humour in the Gunners’ existential catchphrase “Wenger Out!” which itself is a cryptic reference to the Invincibles Season. I’m smirking right now just imagining one of those addlepated simpletons scratching their heads in confusion as Mesut Ozil’s genius wit unfolds itself on their television screens. What fools.. how I pity them.  😂\n And yes, by the way, i DO have an Arsenal tattoo. And no, you cannot see it. It’s for the ladies’ eyes only- and even then they have to demonstrate that they’re within 5 IQ points of my own (preferably lower) beforehand. Nothin personnel kid  😎"
    return body

def wengerSucks():
    wenger = 'wengerSucks.txt'
    with open(wenger,'r') as f:
        content = f.readlines()
    return content

@bot.event
async def on_ready():
    #set playing status
    await bot.change_presence(activity=discord.Game(name='Wengerball'))
    print('Logged on as')
    print(bot.user.name)
    print('----')


@bot.event
async def on_message(message):
    msgLower = message.content.lower()
    banned = bannedThings()

    if message.author == bot.user:
        return
    if msgLower.startswith(prefix):
        if msgLower.startswith(prefix+'help'):
            em = discord.Embed(title='Arsene Wenger Help Message',description=helpMessage())
            await message.channel.send(embed=em)
        if msgLower.startswith(prefix+'table'):
            bg=msgLower.split(' ')
            body = getTable.livetable()
            if len(bg)==1:
              img = Image.new('RGB', (1045, 840), (47,49,54))
              d = ImageDraw.Draw(img)
              font = ImageFont.truetype("AnonymousPro.ttf", 36)
              d.text((5, 10), body, (255,255,255), font=font)
              img.save('tempImg.jpg')
            else:
              if bg[1]=='d' or bg[1]=='dark':
                img = Image.new('RGB', (1045, 840), (47,49,54))
                d = ImageDraw.Draw(img)
                font = ImageFont.truetype("AnonymousPro.ttf", 36)
                d.text((5, 10), body, (255,255,255), font=font)
                img.save('tempImg.jpg')
              elif bg[1]=='l' or bg[1]=='light' or bg[1]=='w' or bg[1]=='white':
                img = Image.new('RGB', (1045, 840), (255,255,255))
                d = ImageDraw.Draw(img)
                font = ImageFont.truetype("AnonymousPro.ttf", 36)
                d.text((5, 10), body, (0,0,0), font=font)
                img.save('tempImg.jpg')

            await message.channel.send("EPL Standings",file=discord.File('tempImg.jpg'))
            
        if msgLower.startswith(prefix+'europa'):
            body = europaTable.main()
            await message.channel.send( '```' + body + '```')
        if msgLower.startswith(prefix+'ping'):
            await message.channel.send('pong')
        if 'tottenham' in msgLower:
            await message.add_reaction('\U0001F4A9')
        if 'spurs' in msgLower:
            await message.add_reaction('\U0001F4A9')
        if 'spuds' in msgLower:
            await message.add_reaction('\U0001F4A9')
        if 'mustafi' in msgLower:
            await message.add_reaction('🔙')
            await message.add_reaction('🔛')
            await message.add_reaction('🔝')
        #if 'craig' in msgLower:
        #    await message.add_reaction('<:fuckcraig:658343402425024552>')
        if msgLower.startswith(prefix+'wengerfact'):
            if str(message.channel) == 'unaifacts':
                await bot.send_message(message.author,"Please don't use "+prefix+"wengerfact in "+str(message.channel))
            else:
                fact = fetchRandomFact('wenger')
                await message.channel.send(fact)
        if msgLower.startswith(prefix+'unaifact'):
            if str(message.channel) == 'unaifacts':
                await bot.send_message(message.author,"Please don't use "+prefix+"unaifact in this channel: "+str(message.channel))
            else:
                fact = fetchRandomFact('unai')
                await message.channel.send(fact)
        if msgLower.startswith(prefix+'artetafact'):
            if str(message.channel) == 'unaifacts':
                await bot.send_message(message.author,"Please don't use "+prefix+"artetafact in "+str(message.channel))
            else:
                fact = fetchRandomFact('arteta')
                await message.channel.send(fact)
        if re.search(r'fixture[s]?$',msgLower[1:]):
            body = findMatches.discordFixtures()
            await message.channel.send('```'+body+'```')
        if re.search(r'fixture[s][ ][\d][\d]?$',msgLower[1:]):
            num = int(msgLower[-2:])
            body = findMatches.discordFixtures(num)
            await message.channel.send('```'+body+'```')
        if re.search(r'next?$',msgLower[1:]):
            body = findMatches.nextFixture()
            await message.channel.send('```'+body+'```')
        if re.search(r'result[s]?$',msgLower[1:]):
            body = findMatches.discordResults()
            await message.channel.send('```'+body+'```')
        if re.search(r'euro[s]?$',msgLower[1:]):
            body = findMatches.getInternationalCup()
            await message.channel.send('```'+body+'```')
        if re.search(r'copa[s]?$',msgLower[1:]):
                body = findMatches.getInternationalCup(44, 20210710)
                await message.channel.send('```'+body+'```')
        if re.search(r'olympic[s]$',msgLower[1:]):
                body = findMatches.getInternationalCup(66, 20210810)
                body = 'Men:\n' + body
                await message.channel.send('```'+body+'```')
                body = findMatches.getInternationalCup(65, 20210810)
                body = 'Women:\n' + body
                await message.channel.send('```'+body+'```')
        #if msgLower.startswith(prefix+'time'):
            #body = schedule.main()
            #await message.channel.send(body)
        #if '💥' in msgLower:
        #    await message.channel.send("💥"+"<:xhaak:531803960680513536><:laca:531803959028088833>")
        if '<:ornstein:346679834501709824>' in msgLower:
            await message.add_reaction('❤')
            await message.add_reaction('ozgasm:332570750290755586')
        if 'brexit' in msgLower:
            await message.add_reaction('brexit:521984465132847104')
        if '<:feelsarsenalman:522208659443417099>' in msgLower:
            await message.add_reaction( 'feelsarsenalman:522208659443417099')
        if '<:feelsinvincibleman:375919858845483008>' in msgLower:
            await message.add_reaction( ':feelsinvincibleman:375919858845483008')
        if '<:nelson:346679834090668034>' in msgLower:
            await message.add_reaction('Bossielny:346679834535264257')
        if msgLower.startswith(prefix+'wengyboi'):
            body = makeWenger(message.content)
            await message.channel.send(body)
        if msgLower.startswith(prefix+'copy'):
            send = copyPasta()
            await message.channel.send(send)
        if msgLower.startswith(prefix+'wengersucks'):
            body = wengerSucks()
            await message.channel.send(body)
        if 'sanchez' in msgLower:
            await message.add_reaction( 'rekt:406186499802136597')
        if any(ele in msgLower for ele in banned):
            await message.delete()
            await message.channel.send("Sorry "+ str(message.author) +" that source is not allowed.")
        if msgLower.startswith(prefix+'clear'):
            if message.author.id == '193393269068136448':
               # clearMessages(message)
                numMsg = int(message.content.split(' ')[1])
                msg = []
                async for x in bot.logs_from(message.channel, limit=numMsg):
                    msg.append(x)        
                await bot.delete_messages(msg)
            else:
                await bot.delete_message(message)


try:
    f = open('token.txt')
    token = f.readline()
    f.close()
    bot.run(token.rstrip())
except Exception as e:
    print (getTimestamp() +"setup error\n")
    print(e)
    sleep(5)
