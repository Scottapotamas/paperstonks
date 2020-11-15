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
# inky_display = InkyWHAT("red")
inky_display = InkyWHAT("black")
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
draw.text((x, y), date_text, inky_display.BLACK, font)

time_text = current_time.strftime("%I:%M %p")
w, h = font.getsize(time_text)
x = inky_display.WIDTH - w
y = 0
draw.text((x, y), time_text, inky_display.BLACK, font)


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
draw.text((anchx-(fw/2), anchy), title_text, inky_display.BLACK, font)
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

draw.text((anchx, anchy), "       DAY   ALL", inky_display.BLACK, font)
anchy = anchy + fh/1.5

offset_mul = 0

for i in range(len(df)):
    line_y = anchy + (offset_mul*fh) + 8
    line_formatted = '{0:<4} {1:>5.1f}% {2:>3.0f}%'.format(df["Code"][i].replace(".AX","").strip(), df["Day %"][i], df["Holding %"][i])
    draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)
    offset_mul = offset_mul + 1

# Left side: Render asx, nasdaq, sp500 'market reference' with percentage
left_x = 100
left_y = 30

anchx = left_x
anchy = left_y

anchx_title = left_x - (fw*16)/1.8 - 8

font = ImageFont.truetype(font_path, 16)
title_text = "ASX 200"
fw, fh = font.getsize(title_text)
draw.text((anchx_title, anchy), title_text, inky_display.BLACK, font)
anchy = anchy + fh - 3

ticker_asx = Ticker("^AXJO")
asx_dict = ticker_asx.price.get("^AXJO")
asx_price = asx_dict.get("regularMarketPrice")
asx_percent = asx_dict.get("regularMarketChangePercent")*100

font = ImageFont.truetype(font_path, 25)
aaord_text = "{0:>+2.2f}% {1:<5.0f}".format(asx_percent, asx_price)
fw, fh = font.getsize(aaord_text)
draw.text((anchx-(fw/2), anchy), aaord_text, inky_display.BLACK, font)
anchy = anchy + fh + 5


font = ImageFont.truetype(font_path, 16)
title_text = "NASDAQ"
fw, fh = font.getsize(title_text)
draw.text((anchx_title, anchy), title_text, inky_display.BLACK, font)
anchy = anchy + fh - 3

ticker_nas = Ticker("^IXIC")
nas_dict = ticker_nas.price.get("^IXIC")
nas_price = nas_dict.get("regularMarketPrice")
nas_percent = nas_dict.get("regularMarketChangePercent")*100

font = ImageFont.truetype(font_path, 25)
nascomp_text = "{0:>+2.2f}% {1:<5.0f}".format(nas_percent, nas_price)
fw, fh = font.getsize(aaord_text)
draw.text((anchx-(fw/2), anchy), nascomp_text, inky_display.BLACK, font)
anchy = anchy + fh + 5

font = ImageFont.truetype(font_path, 16)
title_text = "S&P 500"
fw, fh = font.getsize(title_text)
draw.text((anchx_title, anchy), title_text, inky_display.BLACK, font)
anchy = anchy + fh - 3

ticker_sp = Ticker("^GSPC")
sp_dict = ticker_sp.price.get("^GSPC")
sp_price = sp_dict.get("regularMarketPrice")
sp_percent = sp_dict.get("regularMarketChangePercent")*100

font = ImageFont.truetype(font_path, 25)
spcomp_text = "{0:>+2.2f}% {1:<5.0f}".format(sp_percent, sp_price)
fw, fh = font.getsize(aaord_text)
draw.text((anchx-(fw/2), anchy), spcomp_text, inky_display.BLACK, font)
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


# User specified stocks to monitor
watch_df = pd.read_csv("/home/pi/paperstonks/ticker/watchlist.csv")

watch_price = pd.Series([])
watch_change = pd.Series([])

# Loop through watchlist csv, query pricing info
for i in range(len(watch_df)):
    code_str = watch_df["Code"][i]

    ticker_yahoo = Ticker(code_str)
    price_dict = ticker_yahoo.price.get(code_str)

    watch_price[i] = price_dict.get("regularMarketPrice")
    watch_change[i] = price_dict.get("regularMarketChangePercent")

watch_df.insert(1, "Price", watch_price)
watch_df.insert(1, "Change", watch_change)
watch_df["Day %"] = watch_df["Change"] * 100

font = ImageFont.truetype(font_path, 16)
fw, fh = font.getsize("A")

anchx = left_x - (fw*16)/1.8 - 8
anchy = anchy + 12

offset_mul = 0

for i in range(len(watch_df)):
    line_y = anchy + (offset_mul*fh) + 8
    line_formatted = '{0:<4} {1:>4.1f}% '.format(watch_df["Code"][i].replace(".AX","").strip(), watch_df["Day %"][i])
    draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)
    offset_mul = offset_mul + 1
    if offset_mul % 4 == 0:
        anchx = left_x + 12
        offset_mul = 0

anchy = line_y + 8



# What are trending stocks right now?

# get_trending = get_trending().get("quotes")

# font = ImageFont.truetype(font_path, 16)
# consider_text = "TRENDING"
# fw, fh = font.getsize(consider_text)
# draw.text((anchx, anchy+(fh/2)), consider_text, inky_display.RED, font)
# anchx = anchx + fw + 8

# font = ImageFont.truetype(font_path, 14)
# fw, fh = font.getsize("A")

# line_formatted = '{0:<6} {1:<6}'.format(get_trending[0].get("symbol", None), get_trending[1].get("symbol", None), )
# draw.text((anchx, anchy ), line_formatted, inky_display.BLACK, font)

# anchy = anchy + fh + 4

# line_formatted = '{0:<6} {1:<6}'.format(get_trending[2].get("symbol", None), get_trending[3].get("symbol", None), )
# draw.text((anchx, anchy ), line_formatted, inky_display.BLACK, font)


# Render out the framebuffer
inky_display.set_image(img)
inky_display.show()
