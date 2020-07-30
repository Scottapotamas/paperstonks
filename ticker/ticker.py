


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
inky_display = InkyWHAT("black")
inky_display.set_border(inky_display.WHITE)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

font_path="static/RobotoMono-Bold.ttf"

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
df = pd.read_csv("costbase.csv")

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
right_x = inky_display.WIDTH - 180
right_y = 40

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

for i in range(len(df)):
    line_y = anchy + (i*fh) + 8
    line_formatted = '{0:<4} {1:>5.1f}% {2:>3.0f}%'.format(df["Code"][i].replace(".AX","").strip(), df["Day %"][i], df["Holding %"][i])

    draw.text((anchx, line_y ), line_formatted, inky_display.BLACK, font)



# Left side: Render the ASX200 as 'market reference' with percentage
left_x = 0
left_y = 40

anchx = left_x + 110
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


# Get top gainers/losers
num_notable_to_display = 3

s = Screener()
notable_today = s.get_screeners(['day_gainers_au', 'day_losers_au'], count=num_notable_to_display)
# pprint.pprint(notable_today['day_gainers_au']['quotes'][0]['symbol'])

gainers_sorted = sorted(notable_today['day_gainers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=True)
losers_sorted = sorted(notable_today['day_losers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=False)

print("Top Gainers by %:")
for i in range(0,num_notable_to_display): 
    # Get the human-readable name, if one doesn't exist use the raw code
    stock_name = gainers_sorted[i].get("shortName", None)

    if stock_name == None:
        stock_name = gainers_sorted[i].get("symbol").replace(".AX","").strip()
    else:
        stock_name = stock_name.replace("FPO","").strip()

    print(stock_name,  gainers_sorted[i]['regularMarketChangePercent'])

print("Top Losers by %:")
for i in range(0,num_notable_to_display): 
    stock_name = losers_sorted[i].get("shortName", None)

    if stock_name == None:
        stock_name = losers_sorted[i].get("symbol").replace(".AX","").strip()
    else:
        stock_name = stock_name.replace("FPO","").strip()

    print(stock_name, losers_sorted[i]['regularMarketChangePercent'])


# What are trending stocks right now?
d = get_trending(count=3)
pprint.pprint(d)



# Render out the framebuffer
inky_display.set_image(img)
inky_display.show()
