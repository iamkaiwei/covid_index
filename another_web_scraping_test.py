import finviz
import yfinance as yf
from datetime import datetime
import pandas as pd
import bs4 as bs
import requests

# get time extracted
now = datetime.now()

# Get list of S&P 500 stocks from wikipedia page
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(resp.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})

# Extract the tickers from the table on wikipedia
tickers = []

for row in table.findAll('tr')[1:]:
    ticker = row.findAll('td')[0].text
    tickers.append(ticker)

tickers = list(map(lambda ticker: ticker.replace('\n', '').replace('.', '-'), tickers))
stocks_dic = {}

# Get information from Finviz 
for ticker in tickers:
    print(ticker)
    result = finviz.get_stock(ticker)
    for column, value in result.items():
        if column not in stocks_dic:
            stocks_dic[column] = []
            stocks_dic[column].append(value)
        else:
            stocks_dic[column].append(value)

# Convert result into a data frame to be saved into a csv file
stocks_df = pd.DataFrame(stocks_dic)
stocks_df['datetime extracted'] = now

stocks_df.to_csv('stocks information.csv', index=False)


# # Yahoo Finance
# msft = yf.Ticker("MSFT")
# print(msft.info)