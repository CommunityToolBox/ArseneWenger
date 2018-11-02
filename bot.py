import discord
import datetime,sys,re
import random
from random import randint
import findMatches
import getTable
import europaTable
from time import sleep

prefix = '!'
bot = discord.Client()


def getTimestamp():
    dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
    hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
    min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
    t = '[' + hr + ':' + min + '] '
    return dt + t

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

def helpMessage():
    help = '```\n'
    help += prefix+'help\nDisplay this message.\n'
    help += prefix+'table\nDisplay the current Premier League Table.\n'
    help += prefix+'europa\nDisplay the Europa League table.\n'
    help += prefix+'wengerfact\nGet a random fact about our lord and savior Arsene Wenger.\n'
    help += prefix+'unaifact\nGet a random fact about our manager Unai Emery.\n'
    help += prefix+'fixtures\nDisplay the next 3 fixtures.\n'
    help += prefix+'wengyboi <#>\nMake a wengyboi of # length! Max 10.\n'
    help += '```'
    return help

def makeWenger(message):
    message = message.split(' ')[1]
    if int(message) > 10:
        message = 10
    body = '<:ArseneTop:346679833020989440>\n'
    for i in range(0,int(message)):
        body += '<:ArseneMid:351696622171979776>\n'
    body += '<:ArseneBot:346679833377636363>\n'
    return body

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
    wenger = '/root/discord/arseneWenger/wengerSucks.txt'
    with open(wenger,'r') as f:
        content = f.readlines()
    return content

@bot.event
async def on_ready():
    #set playing status
    await bot.change_presence(game=discord.Game(name='Wengerball'))
    print('Logged on as')
    print(bot.user.name)
    print('----')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower().startswith(prefix+'help'):
        em = discord.Embed(title='Arsene Wenger Help Message',description=helpMessage())
        await bot.send_message(message.channel,embed=em)
    if message.content.lower().startswith(prefix+'table'):
        body = getTable.discordMain()
        await bot.send_message(message.channel, '```' + body + '```')
    if message.content.lower().startswith(prefix+'europa'):
        body = europaTable.main()
        await bot.send_message(message.channel, '```' + body + '```')
    if message.content.lower().startswith(prefix+'ping'):
        await bot.send_message(message.channel, 'pong')
    if 'tottenham' in message.content.lower():
        await bot.add_reaction(message,'\U0001F4A9')
    if message.content.lower().startswith(prefix+'wengerfact'):
        if str(message.channel) == 'unaifacts':
            await bot.send_message(message.author,"Please don't use "+prefix+"wengerfact in "+message.channel)
        else:
            fact = wengerFact()
            await bot.send_message(message.channel,fact)
    if message.content.lower().startswith(prefix+'unaifact'):
        if str(message.channel) == 'unaifacts':
            await bot.send_message(message.author,"Please don't use "+prefix+"unaifact in this "+message.channel)
        else:
            fact = unaiFact()
            await bot.send_message(message.channel,fact)
    if message.content.lower().startswith(prefix+'fixture'):
        body = findMatches.discordFixtures()
        await bot.send_message(message.channel,'```'+body+'```')
    if message.content.lower().startswith(prefix+'results'):
        body = findMatches.discordResults()
        await bot.send_message(message.channel,'```'+body+'```')
    if '💥' in message.content.lower():
        await bot.send_message(message.channel,"💥"+"<:xhaka:341950939902509056><:laca:341950939055259650>")
    if '<:ornstein:346679834501709824>' in message.content.lower():
        await bot.add_reaction(message,'❤')
        await bot.add_reaction(message,'ozgasm:332570750290755586')
    if 'brexit' in message.content.lower():
        await bot.add_reaction(message,'brexit:476534538269622272')
    if '<:feelsarsenalman:339379360983416833>' in message.content.lower():
        await bot.add_reaction(message, 'feelsarsenalman:339379360983416833')
    if '<:feelsinvincibleman:375919858845483008>' in message.content.lower():
        await bot.add_reaction(message, ':feelsinvincibleman:375919858845483008')
    if '<:nelson:346679834090668034>' in message.content.lower():
        await bot.add_reaction(message,'Bossielny:346679834535264257')
    if message.content.lower().startswith(prefix+'wengyboi'):
        body = makeWenger(message.content)
        await bot.send_message(message.channel,body)
    if message.content.lower().startswith(prefix+'copy'):
        await bot.send_message(message.channel,copyPasta())
    if message.content.lower().startswith(prefix+'wengersucks'):
        body = wengerSucks()
        print(body)
        await bot.send_message(message.channel,body)
    if 'sanchez' in message.content.lower():
        await bot.add_reaction(message, 'rekt:406186499802136597')
    if message.content.lower().startswith(prefix+'clear'):
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
except:
    print (getTimestamp() +"setup error\n")
    sleep(5)
