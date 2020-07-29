#!/usr/bin/env python3
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import pprint

from yahooquery import Ticker, Screener
from yahooquery import get_trending

print("Super Stonk Summariser")

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

print(df.head(10))

# Get top gainers/losers
num_notable_to_display = 3

s = Screener()
notable_today = s.get_screeners(['day_gainers_au', 'day_losers_au'], count=num_notable_to_display)
# pprint.pprint(notable_today['day_gainers_au']['quotes'][0]['symbol'])

gainers_sorted = sorted(notable_today['day_gainers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=True)
loseers_sorted = sorted(notable_today['day_losers_au']['quotes'], key=lambda k: k['regularMarketChangePercent'], reverse=True)

print("Top Gainers by %:")
for i in range(0,num_notable_to_display): 
    print(gainers_sorted[i]['symbol'].replace(".AX",""), gainers_sorted[i]['shortName'], gainers_sorted[i]['regularMarketChangePercent'])

print("Top Losers by %:")
for i in range(0,num_notable_to_display): 
    print(loseers_sorted[i]['symbol'].replace(".AX",""), loseers_sorted[i]['shortName'], loseers_sorted[i]['regularMarketChangePercent'])


# What are trending stocks right now?
d = get_trending(count=3)
pprint.pprint(d)