#!/usr/bin/env python3
import pandas as pd
import datetime
# import matplotlib.pyplot as plt
import pprint

from yahooquery import Ticker, Screener
from yahooquery import get_trending

from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw

print("Super Stonk Summariser")

# Setup the display
inky_display = InkyWHAT("red")
inky_display.set_border(inky_display.WHITE)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

font_path="/home/pi/paperstonks/ticker/static/RobotoMono-Bold.ttf"

# Get and format date/time for the titlebar
current_time = datetime.datetime.now()  

font = ImageFont.truetype(font_path, 16)
date_text = current_time.strftime("%d %B")
x = 0
y = 0
draw.text((x, y), date_text, inky_display.RED, font)

time_text = current_time.strftime("%I:%M %p")
w, h = font.getsize(time_text)
x = inky_display.WIDTH - w
y = 0
draw.text((x, y), time_text, inky_display.RED, font)


# Read the user's list of shares with cost-base information
df = pd.read_csv("/home/pi/paperstonks/ticker/costbase.csv")

first_price = pd.Series([]) 
last_price = pd.Series([]) 

# Loop through codes and query current pricing info
for i in range(len(df)): 
    code_str = df["Code"][i]

    ticker_yahoo = Ticker(code_str)
    price_dict = ticker_yahoo.price.get(code_str)

    first_price[i] = price_dict.get("regularMarketOpen")
    last_price[i] = price_dict.get("regularMarketPrice")

# Insert new columns from the queries
df.insert(3, "Open Price", first_price)         
df.insert(4, "Market Price", last_price) 

# Calculate average cost base, current value
df["Net Basis"]  = df["Quantity"] * df["NetAvg"]
df["Current Value"]  = df["Quantity"] * df["Market Price"]

# Calulate percentage changes
df["Holding %"] = (df["Current Value"] - df["Net Basis"] )/df["Net Basis"]  * 100
df["Day %"] = (df["Market Price"] - df["Open Price"] )/df["Open Price"]  * 100

# Sort by percentage change today
df.sort_values(by=['Day %'], inplace=True, ascending=False)

# Calculate portfolio value and percentage portfolio change since basis
holdings_invested = df["Net Basis"].sum() 
holdings_current = df["Current Value"].sum()
portfolio_change = (holdings_current - holdings_invested )/holdings_invested  * 100


# Right Side of display shows the portfolio value and stock breakdown
right_x = inky_display.WIDTH - 170
right_y = 30

# Print the total day change and all time change
anchx = right_x + (inky_display.WIDTH - right_x)/2 
anchy = right_y

font = ImageFont.truetype(font_path, 18)
title_text = "HOLDINGS"
fw, fh = font.getsize(title_text)
draw.text((anchx-(fw/2), anchy), title_text, inky_display.RED, font)
anchy = anchy + fh

font = ImageFont.truetype(font_path, 30)
profit_text = "{0:+0.2f}%".format(portfolio_change)
fw, fh = font.getsize(profit_text)
draw.text((anchx-(fw/2), anchy), profit_text, inky_display.BLACK, font)
anchy = anchy + fh

# Print the portfolio gain table
font = ImageFont.truetype(font_path, 16)
fw, fh = font.getsize("A")

right_x + (inky_display.WIDTH - right_x)/2 

anchx = right_x + (inky_display.WIDTH - right_x)/2 - (fw*16)/2
anchy = anchy + 8

draw.text((anchx, anchy), "       DAY   ALL", inky_display.RED, font)
anchy = anchy + fh/1.5

offset_mul = 0

for i in range(len(df)):
    line_y = anchy + (offset_mul*fh) + 8
    line_formatted = '{0:<4} {1:>5.1f}% {2:>3.0f}%'.format(df["Code"][i].replace(".AX","").strip(), df["Day %"][i], df["Holding %"][i])
    draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)
    offset_mul = offset_mul + 1

# Left side: Render the ASX200 as 'market reference' with percentage
left_x = 100
left_y = 30

anchx = left_x
anchy = left_y

font = ImageFont.truetype(font_path, 18)
title_text = "S&P/ASX 200"
fw, fh = font.getsize(title_text)
draw.text((anchx-(fw/2), anchy), title_text, inky_display.RED, font)
anchy = anchy + fh

ticker_asx = Ticker("^AXJO")
asx_dict = ticker_asx.price.get("^AXJO")
asx_price = asx_dict.get("regularMarketPrice")
asx_percent = asx_dict.get("regularMarketChangePercent")*100

font = ImageFont.truetype(font_path, 30)
aaord_text = "{0:0.0f} {1:+0.2f}%".format(asx_price, asx_percent)
fw, fh = font.getsize(aaord_text)
draw.text((anchx-(fw/2), anchy), aaord_text, inky_display.BLACK, font)
anchy = anchy + fh


# Get other market summary items

ticker_gold = Ticker("GC=F")
gold = ticker_gold.price.get("GC=F").get("regularMarketPrice")

ticker_oil = Ticker("CL=F")
oil = ticker_oil.price.get("CL=F").get("regularMarketPrice")

ticker_btc = Ticker("BTC-AUD")
btc = ticker_btc.price.get("BTC-AUD").get("regularMarketPrice")

ticker_aud = Ticker("AUDUSD=X")
aud = ticker_aud.price.get("AUDUSD=X").get("regularMarketPrice")

# Render below the ASX text

commodities_text = "{0:<4}{1:>5.0f}  {2:<4}{3:>4.1f}".format("GOLD", gold, "OIL", oil)
currencies_text = "{0:<4}{1:>5.2f}  {2:<4}{3:>4.1f}k".format("AUD", aud, "BTC", btc/1000)

font = ImageFont.truetype(font_path, 16)
fw, fh = font.getsize(commodities_text)
anchy = anchy + 8
draw.text((anchx - (fw/2), anchy), commodities_text, inky_display.BLACK, font)
anchy = anchy + fh

draw.text((anchx - (fw/2), anchy), currencies_text, inky_display.BLACK, font)
anchy = anchy + fh



# Get top gainers/losers
num_notable_to_display = 3

s = Screener()
notable_today = s.get_screeners(['day_gainers_au', 'day_losers_au'], count=8)

gainers_sorted = sorted(notable_today['day_gainers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=True)
losers_sorted = sorted(notable_today['day_losers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=False)

# Render the top gainers/losers 
font = ImageFont.truetype(font_path, 16)
fw, fh = font.getsize("A")

anchx = left_x - (fw*16)/1.8
anchy = anchy + 12

# Top Gainers
stock_i = 0
valid_i = 0
while valid_i <= (num_notable_to_display-1):
     # Get the human-readable name, if one doesn't exist use the raw code
    stock_name = gainers_sorted[stock_i].get("shortName", None)

    # TODO consider walking the list and filtering on market cap

    if stock_name == None:
        stock_name = gainers_sorted[stock_i].get("symbol").replace(".AX","").strip()
    else:
        stock_name = stock_name.replace("FPO","").strip()

    stock_price = gainers_sorted[stock_i]['regularMarketChangePercent']
    if stock_price >= 100:
        price_string = '{0:>+5.1f}x'.format(stock_price/100.0)
    else:
        price_string = '{0:>+5.1f}%'.format(stock_price)

    stock_i += 1

    # Clamp maximum daily increase, over 5x is more likely an error or irrelevant subcent-stock
    if stock_price <= 500:
        line_y = anchy + (valid_i*fh) + 8
        line_formatted = '{0:<10} {1}'.format(stock_name, price_string)
        draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)
        valid_i += 1

anchy = line_y + 8

# Top Losers
for i in range(0,num_notable_to_display): 
    # Get the human-readable name, if one doesn't exist use the raw code
    stock_name = losers_sorted[i].get("shortName", None)

    if stock_name == None:
        stock_name = losers_sorted[i].get("symbol").replace(".AX","").strip()
    else:
        stock_name = stock_name.replace("FPO","").strip()

    stock_price = losers_sorted[i]['regularMarketChangePercent']
    price_string = '{0:>+5.1f}%'.format(stock_price)

    line_y = anchy + (i*fh) + 8
    line_formatted = '{0:<10} {1}'.format(stock_name, price_string)
    draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)

anchy = line_y + 30

# What are trending stocks right now?
get_trending = get_trending().get("quotes")

font = ImageFont.truetype(font_path, 16)
consider_text = "CONSIDER"
fw, fh = font.getsize(consider_text)
draw.text((anchx, anchy+(fh/2)), consider_text, inky_display.RED, font)
anchx = anchx + fw + 8

font = ImageFont.truetype(font_path, 14)
fw, fh = font.getsize("A")

line_formatted = '{0:<6} {1:<6}'.format(get_trending[0].get("symbol", None), get_trending[1].get("symbol", None), )
draw.text((anchx, anchy ), line_formatted, inky_display.BLACK, font)

anchy = anchy + fh + 4

line_formatted = '{0:<6} {1:<6}'.format(get_trending[2].get("symbol", None), get_trending[3].get("symbol", None), )
draw.text((anchx, anchy ), line_formatted, inky_display.BLACK, font)

# Render out the framebuffer
inky_display.set_image(img)
inky_display.show()
