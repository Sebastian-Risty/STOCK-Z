import discord
from discord.ext import commands
from scraper_api import ScraperAPIClient
from datetime import datetime
import requests
import json
import random


#credit: https://jereze.com/code/image-search-api/ for image search idea/reference

client = ScraperAPIClient('')
activityText = "Stockz"
activity = discord.Activity(type=discord.ActivityType.watching, name=activityText)

bot = commands.Bot(command_prefix='~')
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=activity)

#stocks
@bot.command()
async def s(ctx, symbol = 'TSLA', type = 'close', func = 'TIME_SERIES_INTRADAY', interval = '5min', time = '', aliases = ["stocks"]):
    stockCall = requests.get('https://www.alphavantage.co/query?function='+func+'&symbol='+symbol+'&interval='+interval+'&apikey=')
    stockDict = json.loads(stockCall.text)

    if(time == ''):
        time = stockDict["Meta Data"]["3. Last Refreshed"]

    if(type == 'volume'):
        info = '```'+ str(round(int(stockDict['Time Series (' + interval + ')'][time]['5. volume']), 0)) + '```'
    elif(type == 'close'):
        info = '```$' + str(round(float(stockDict['Time Series (' + interval + ')'][time]['4. close']), 3)) + '```'
    elif(type == 'low'):
        info = '```$' + str(round(float(stockDict['Time Series (' + interval + ')'][time]['3. low']), 3)) + '```'
    elif(type == 'high'):
        info = '```$' +str(round(float(stockDict['Time Series (' + interval + ')'][time]['2. high']), 3)) + '```'
    elif(type == 'open'):
        info = '```$' + str(round(float(stockDict['Time Series (' + interval + ')'][time]['1. open']), 3)) + '```'

    embed = discord.Embed(color = discord.Color.red())
    embed.set_author(name='STOCKZ')
    embed.add_field(name=symbol + ' ' + type, value = info, inline = False)
    embed.add_field(name = 'Refresh Time' , value = time + ' ' + stockDict["Meta Data"]["6. Time Zone"], inline = False)
    img = client.get(url = 'https://api.qwant.com/api/search/images/?count=5&q='+ symbol + ' logo' +'&t=images&safesearch=1&locale=en_US&uiv=4').text
    imgDict = json.loads(img)
    response = imgDict['data']['result']['items']
    urls = [img.get('media') for img in response]
    embed.set_thumbnail(url=urls[0])
    await ctx.send(embed=embed)

#crypto
@bot.command()
async def c(ctx, symbol = 'BTC',type = 'close', market = 'USD', func = 'Daily', date = '', aliases = ["crypto"]):
    #func = func.upper()
    cryptoCall = requests.get('https://www.alphavantage.co/query?function='+'DIGITAL_CURRENCY_'+func.upper()+'&symbol='+symbol+'&market='+market+'&apikey=')
    cryptoDict = json.loads(cryptoCall.text)

    if(date == ''):
        date = cryptoDict["Meta Data"]["6. Last Refreshed"]

    if(type == 'volume'):
        info = '```'+ str(round(int(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['5. volume']), 8)) +" "+ market + '```'
    elif(type == 'close'):
        info = '```' + str(round(float(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['4a. close'+' ('+market+')']), 8)) +" "+ market + '```'
    elif(type == 'low'):
        info = '```' + str(round(float(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['3a. low'+' ('+market+')']), 8)) +" "+ market + '```'
    elif(type == 'high'):
        info = '```' +str(round(float(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['2a. high'+' ('+market+')']), 8)) +" "+ market + '```'
    elif(type == 'open'):
        info = '```' + str(round(float(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['1a. open'+' ('+market+')']), 8)) +" "+ market + '```'
    elif(type == 'market'):
        info = '```$' + str(round(float(cryptoDict['Time Series (Digital Currency ' + func + ')'][date[0:10]]['6. market cap'+' ('+market+')']), 8)) +" "+ market + '```'
    
    embed = discord.Embed(color = discord.Color.blue())
    embed.set_author(name='STOCKZ')
    embed.add_field(name=symbol + ' ' + type, value = info, inline = False)
    embed.add_field(name = 'Refresh Time' , value = date + ' ' + cryptoDict["Meta Data"]["7. Time Zone"], inline = False)
    img = client.get(url = 'https://api.qwant.com/api/search/images/?count=5&q='+ cryptoDict["Meta Data"]["3. Digital Currency Name"] + ' logo' +'&t=images&safesearch=1&locale=en_US&uiv=4').text
    imgDict = json.loads(img)
    response = imgDict['data']['result']['items']
    urls = [img.get('media') for img in response]
    embed.set_thumbnail(url=urls[0])
    await ctx.send(embed=embed)

#exchange
#fix thingy
@bot.command()
async def ce(ctx, from_currency = 'BTC', to_currency = 'USD'):
    exchangeCall = requests.get('https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE'+'&from_currency='+from_currency+'&to_currency='+to_currency+'&apikey=')
    exchangeDict = json.loads(exchangeCall.text)
    embed = discord.Embed(color = discord.Color.from_rgb(255,255,0))
    embed.set_author(name='STOCKZ')
    embed.add_field(name=exchangeDict['Realtime Currency Exchange Rate']['2. From_Currency Name']+' to '+exchangeDict['Realtime Currency Exchange Rate']['4. To_Currency Name'], value=exchangeDict['Realtime Currency Exchange Rate']['5. Exchange Rate'], inline=False)
    embed.add_field(name = 'Refresh Time' , value = exchangeDict['Realtime Currency Exchange Rate']['6. Last Refreshed'] + ' ' + exchangeDict['Realtime Currency Exchange Rate']['7. Time Zone'], inline = False)
    await ctx.send(embed=embed)

#crypto health
@bot.command()
async def ch(ctx, symbol = 'BTC', aliases = ["cryptoh", "cryptohealth"]):
    cryptoHealthRequest = requests.get('https://www.alphavantage.co/query?function=CRYPTO_RATING&symbol='+symbol+'&apikey=')
    cryptoHealthDict = json.loads(cryptoHealthRequest.text)
    rating = cryptoHealthDict['Crypto Rating (FCAS)']['4. fcas score']

    if(int(rating) >= 900):
        embed = discord.Embed(color = discord.Color.from_rgb(0, 230, 133))
    elif(int(rating) >= 750):
        embed = discord.Embed(color = discord.Color.from_rgb(115, 239, 187))
    elif(int(rating) >= 650):
        embed = discord.Embed(color = discord.Color.from_rgb(191, 239, 219))
    elif(int(rating) >= 500):
        embed = discord.Embed(color = discord.Color.from_rgb(255, 172, 112))
    else:
        embed = discord.Embed(color = discord.Color.from_rgb(255, 77, 77))

    embed.set_author(name='STOCKZ')
    embed.add_field(name=symbol, value = 'FCAS Score: '+rating+'\nDeveloper Score: '+cryptoHealthDict['Crypto Rating (FCAS)']['5. developer score']+'\nMarket Maturity Score: '+cryptoHealthDict['Crypto Rating (FCAS)']['6. market maturity score']+'\nUtility Score: '+cryptoHealthDict['Crypto Rating (FCAS)']['7. utility score'], inline = False)
    embed.add_field(name='Refresh Time', value = cryptoHealthDict['Crypto Rating (FCAS)']['8. last refreshed'] + ' ' + cryptoHealthDict['Crypto Rating (FCAS)']['9. timezone'], inline = False)
    img = client.get(url = 'https://api.qwant.com/api/search/images/?count=5&q='+ cryptoHealthDict["Crypto Rating (FCAS)"]["2. name"] + ' logo' +'&t=images&safesearch=1&locale=en_US&uiv=4').text
    imgDict = json.loads(img)
    response = imgDict['data']['result']['items']
    urls = [img.get('media') for img in response]
    embed.set_thumbnail(url=urls[0])
    await ctx.send(embed=embed)

#help
@bot.command()
async def h(ctx, command = '', aliases = ["help"]):
    author = ctx.message.author
    embed = discord.Embed(color = discord.Color.red())
    if(author.id == ):
        embed.set_author(name='Welcome Admin')
        embed.add_field(name='Roles', value='')
    if(command == ''):
        embed.set_author(name='General Command Help')
        embed.add_field(name='API Documentation', value = 'https://www.alphavantage.co/documentation/#', inline = False)
        embed.add_field(name='~help', value='brings you here', inline = False)
        embed.add_field(name='~s (STOCKS)', value='symbol | type | function | interval | time || \'~help s\' for more help', inline = False)
        embed.add_field(name='~c (CRYPTO)', value='symbol | type | market | function | date || \'~help c\' for more help', inline = False)
        embed.add_field(name='~ch (CRYPTO Health Value)', value='symbol || \'~help ch\' for more help', inline = False)
        #ce
    elif(command == 's'):
        embed.set_author(name='Command Help (~s)')
        embed.add_field(name='API Documentation', value = 'https://www.alphavantage.co/documentation/#', inline = False)
        embed.add_field(name='symbol', value = 'ticker/stock symbol, the equity of your choice. EX: TSLA, IBM, GOOG, DBS. *should be all uppercase* *NASDAQ ONLY*', inline = False)
        embed.add_field(name='type', value = 'OHLC + Volume. EX: open, high, low, close, volume. *should be all lowercase*', inline = False)
        embed.add_field(name='function', value = 'the timeseries to be used. EX: \nTIME_SERIES_DAILY\n TIME_SERIES_DAILY_ADJUSTED\n TIME_SERIES_WEEKLY\n TIME_SERIES_WEEKLY_ADJUSTED\n TIME_SERIES_MONTHLY\n TIME_SERIES_MONTHLY_ADJUSTED', inline = False)
        embed.add_field(name='interval', value = 'time interval between two consecutive data points. values supported are: 1min, 5min, 15min, 30min, 60min. Directly effects the time input, EX: 15min requires even intervals from 00:00 (19:15:00, 19:30:00, etc...)', inline = False)
        embed.add_field(name='time', value = 'the exact time you want to grab the OHLC from. Format is as follows:\n yyyy-mm-dd hh:mm:ss (time is in 24 hour format)', inline = False)
    elif(command == 'c'):
        embed.set_author(name='Command Help (~c)')
        embed.add_field(name='API Documentation', value = 'https://www.alphavantage.co/documentation/#', inline = False)
        embed.add_field(name='TODO', value='TODO', inline = False)
    elif(command == 'ce'):
        embed.set_author(name='Command Help (~ce)')
        embed.add_field(name='API Documentation', value = 'https://www.alphavantage.co/documentation/#', inline = False)
        embed.add_field(name='TODO', value='TODO', inline = False)
    elif(command == 'ch'):
        embed.set_author(name='Command Help (~ch)')
        embed.add_field(name='API Documentation', value = 'https://www.alphavantage.co/documentation/#', inline = False)
        embed.add_field(name='TODO', value='TODO', inline = False)
    #await ctx.send('check your dm\'s (;')

    await author.send(embed=embed)

#image lookup
@bot.command()
async def image(ctx, *, arg):
    img = client.get(url = 'https://api.qwant.com/api/search/images/?count=5&q='+ arg +'&t=images&safesearch=1&locale=en_US&uiv=4').text
    imgDict = json.loads(img)
    response = imgDict['data']['result']['items']
    urls = [img.get('media') for img in response]
    await ctx.send(urls[random.randint(0, len(urls)-1)])

#----------#
#role info
@bot.command()
async def roles(ctx, *, arg, aliases = ["role", "r"]):
    i = 1
    k = 1
    embed = discord.Embed(color = discord.Color.red())
    embed.set_author(name='Discord Roles Info @ ' + ctx.guild.name)
    author = ctx.message.author
    if(author.id != ):
        return
    else:
        if(arg == 'list'):
            roleList = []
            for role in ctx.guild.roles:
                roleAtributes = [role.name, role.color.to_rgb(), role.id]
                roleList.append(roleAtributes)
                #https://discordpy.readthedocs.io/en/latest/api.html#discord.Role
        for role in roleList[1:len(roleList)]:
            embed.add_field(name='```'+roleList[i][0]+'```', value='** **', inline = False)
            k = 1
            for attribute in role:
                if(k == 1):
                    embed.add_field(name='**Color: **'+str(roleList[i][k]), value='\u200b', inline = False)
                if(k == 2):
                    embed.add_field(name='**ID: **'+str(roleList[i][k]), value='\u200b', inline = False)
                #add more if needed
                k += 1
            i += 1
        embed.add_field(name='** **', value='** **', inline = True)
        await author.send(embed=embed)
        #fix output format

#discord vs guild join date
@bot.command()
async def test(ctx, arg):

    if(ctx.message.author.id != ):
        return
    member = ctx.guild.get_member(int(arg))
    await ctx.send('Server join date: '+str(member.joined_at.strftime("%x"))+'\nDiscord join date: '+str(member.created_at))

#guessing game
@bot.command()
async def guess(ctx):
    answer = random.randint(1,11)
    number_of_guesses = 0
    while number_of_guesses < 3:
        if(number_of_guesses == 0):
            await ctx.send('take a guess 1-10!')
        else:
            await ctx.send('guess again!')

        player_answer = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
        try:
            player_answer = int(player_answer.content)
        except ValueError:
            await ctx.send("Invalid: Your asnwer should be an integer number")
            number_of_guesses -= 1
            continue
        number_of_guesses += 1
        if player_answer == answer:
            break
        elif player_answer >= 11:
            await ctx.send("Invalid: Your asnwer should be 10 and below")
            number_of_guesses -= 1
            continue
        elif player_answer < answer:
            await ctx.send("Your answer is too low")
            continue
        elif player_answer > answer:
            await ctx.send("Your answer is too high")
            continue

    if player_answer == answer:
        await ctx.send("You guessed the answer correctly")
    else:
        await ctx.send("You guessed the answer wrong\nThe answer was: "+str(answer))

#NASA picture of the day
@bot.command()
async def apod(ctx, date=str(datetime.date(datetime.now()))):
    apodRequest = requests.get('https://api.nasa.gov/planetary/apod?date='+date+'&api_key=')
    embed = discord.Embed(color = discord.Color.blue())
    description = apodRequest.json().get('explanation')
    embed.description = description
    if(apodRequest.json().get('code') == 400 or apodRequest.json().get('code') == 404):
        embed.add_field(name='Error!', value=apodRequest.json().get('msg'), inline=False)
        await ctx.send(embed=embed)
        return
    if(description.find('Comet NEOWISE Images') != -1):
        description = description[:description.find('Comet NEOWISE Images')]
    elif description.find("Notable Images of Comet NEOWISE Submitted to APOD:") != -1:
        description = description[:description.find("Notable Images of Comet NEOWISE Submitted to APOD:")]
    embed = discord.Embed(color = discord.Color.blue(), description=description)
    embed.set_author(name=apodRequest.json().get('title'))
    if(apodRequest.json().get('media_type') == 'video'):
        embed.description = description + '\n\n' + apodRequest.json().get('url')
        await ctx.send(embed=embed)
        return
    embed.set_image(url=apodRequest.json().get('hdurl'))
    if(apodRequest.json().get('copyright') != None):
        embed.set_footer(text=apodRequest.json().get('copyright'))
    await ctx.send(embed=embed)


print('Running!')
bot.run('')


