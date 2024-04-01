import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

yf.pdr_override()
from datetime import datetime

File = "List"


def tickerMakeNS(tickers):
    for ticker in tickers:
        tickerNS = ticker + ".NS"
        print(tickerNS)
        RSI(tickerNS, Dict, ticker)


def RSI(tickerNS, Dict, ticker):

    days = 14

    startdate = datetime(2022, 1, 1)


    data = pdr.get_data_yahoo(tickerNS, start=startdate)

    delta = data["Close"].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    average_up = up.ewm(com=(days - 1), adjust=False).mean()
    average_down = down.ewm(com=(days - 1), adjust=False).mean()
    rs = average_up / average_down

    data["RSI"] = 100 - (100 / (1 + rs))

    data = data.iloc[days:]

    data = data["RSI"]
    datalast = data.iloc[-1]
    dataPrev2 = data.iloc[-2]
    dataPrev3 = data.iloc[-3]
    dataPrev4 = data.iloc[-4]
    dataPrev5 = data.iloc[-5]

    datalast = round(datalast, 2)
    dataPrev2 = round(dataPrev2, 2)
    dataPrev3 = round(dataPrev3, 2)
    dataPrev4 = round(dataPrev4, 2)
    dataPrev5 = round(dataPrev5, 2)

    Dict.update({str(ticker): [datalast, dataPrev2, dataPrev3, dataPrev4, dataPrev5]})


def STOCKS(list):

    print("LOADING...Please wait")

    tickers_1 = []

    tickers_bse = []

    f = open(f"{list}.txt")
    data = f.read()
    tickers_bse = data.split("//")
    tickers_1 = tickers_bse[0].split(",")

    tickers_bse = tickers_bse[1].split(",")
    f.close()

    if len(tickers_1) != 0 and tickers_1[0] != "":
        tickerMakeNS(tickers_1)

    if len(tickers_bse) != 0 and tickers_bse[0] != "":
        for ticker in tickers_bse:
            ticker_BO = ticker + ".BO"
            RSI(ticker_BO, Dict, ticker)


Dict = {}
fordown = {}
STOCKS(File)

buy = []
sell = []
hold = []
nothold = []

print(Dict)
Dict = dict(sorted(Dict.items(), reverse=True, key=lambda item: item[1][0]))
print(Dict)

for key, value in Dict.items():
    if (value[0] >= 67.5) and (
        (value[0] < value[1] < value[2]) or (value[0] < value[2])
    ):
        sell.append(f"{key} : {value[0]}")

    elif (value[0] <= 33.5) and (
        (value[0] > value[1] > value[2]) or (value[0] > value[2])
    ):
        buy.append(f"{key} : {value[0]}")

    elif (
        (value[0] < value[1] < value[2] < value[3] < value[4])
        or (value[0] < value[1] < value[2] < value[3])
        or (value[0] < value[1] < value[2])
        or (value[0] < value[1] < value[2] < value[4])
        or (value[0] < value[1] < value[3] < value[4])
        or (value[0] < value[2] < value[3] < value[4])
        or (value[1] < value[2] < value[3] < value[4])
        or (value[0] < value[1] < value[3])
        or (value[0] < value[2] < value[3])
        or (value[0] < value[3] < value[4])
        or (value[0] < value[1] < value[4])
    ):

        nothold.append(f"{key} : {value[0]}")

    else:
        hold.append(f"{key} : {value[0]}")

if len(buy) > 1:
    buy.reverse()

length = []
length.append(len(buy))
length.append(len(sell))
length.append(len(hold))
length.append(len(nothold))
length.sort(reverse=True)

if length[0] > len(buy):
    var = length[0] - len(buy)
    for i in range(var):
        buy.append(" ")

if length[0] > len(sell):
    var = length[0] - len(sell)
    for i in range(var):
        sell.append(" ")

if length[0] > len(hold):
    var = length[0] - len(hold)
    for i in range(var):
        hold.append(" ")

if length[0] > len(nothold):
    var = length[0] - len(nothold)
    for i in range(var):
        nothold.append(" ")

stocks = {}
stocks.update({"    BUY       ": buy})
stocks.update({"    SELL       ": sell})
stocks.update({"    HOLD       ": hold})
stocks.update({"    DOWN       ": nothold})

stocks = pd.DataFrame(stocks)

stocks.index += 1

table = stocks.to_string()

file = open("Table.txt", "w")
file.write(table)
print("\n")
print(table)
file.close()

# stocks.to_excel('RSI.xlsx')
