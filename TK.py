import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

yf.pdr_override()

class StockAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Stock Analyzer")

        self.label = tk.Label(master, text="Enter File Name:")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.analyze_button = tk.Button(master, text="Analyze", command=self.analyze_stocks)
        self.analyze_button.pack()

        self.result_text = tk.Text(master, height=20, width=80)
        self.result_text.pack()

    def tickerMakeNS(self, tickers):
        for ticker in tickers:
            tickerNS = ticker + ".NS"
            self.RSI(tickerNS, ticker)

    def RSI(self, tickerNS, ticker):
        startdate = datetime(2022, 1, 1)
        enddate = datetime(2023,11,1)
        data = pdr.get_data_yahoo(tickerNS, start=startdate, end=enddate)

       

        momentum_period = 20
        bars_back = 150
        days = 14
        gap = 10
        RSIUpper = 61
        RSILower = 35

        # Calculate Momentum
        data['Momentum'] = data["Close"].diff(momentum_period - 1)

        #RSi calclate
        delta = data["Close"].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        average_up = up.ewm(com=(days - 1), adjust=False).mean()
        average_down = down.ewm(com=(days - 1), adjust=False).mean()
        rs = average_up / average_down
        rsi = 100 - (100 / (1 + rs))
        data["RSI"] = rsi
        # data = data.iloc[days:]
        


        datalast = data["RSI"].iloc[-1]
        dataPrev2 = data["RSI"].iloc[-2]
        dataPrev3 = data["RSI"].iloc[-3]
        dataPrev4 = data["RSI"].iloc[-4]
        dataPrev5 = data["RSI"].iloc[-5]
        datalast = round(datalast, 2)
        dataPrev2 = round(dataPrev2, 2)
        dataPrev3 = round(dataPrev3, 2)
        dataPrev4 = round(dataPrev4, 2)
        dataPrev5 = round(dataPrev5, 2)
        self.Dict.update({str(ticker): [datalast, dataPrev2, dataPrev3, dataPrev4, dataPrev5]})

        # Identify Divergence Points
        divergence_points = []
        for i in range(days+1, len(data)):

            momentumBool = data["Close"].iloc[i - days] > data["Close"].iloc[i] and data['Momentum'].iloc[i - days] > data['Momentum'].iloc[i]
            RSIBool = data["RSI"].iloc[i] < RSILower

            if RSIBool and  momentumBool:
                divergence_points.append((data.index[i], data['Close'].iloc[i]))

        if len(divergence_points) !=0:
            divergence_dates, divergence_prices = zip(*divergence_points)
        print(divergence_points)
        print(data)


    def STOCKS(self, file_name):
        tickers_1 = []
        tickers_bse = []
        try:
            with open(f"{file_name}.txt") as f:
                data = f.read()
                tickers_bse = data.split("//")
                tickers_1 = tickers_bse[0].split(",")
                tickers_bse = tickers_bse[1].split(",")
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found!")
            return
        if len(tickers_1) != 0 and tickers_1[0] != "":
            self.tickerMakeNS(tickers_1)

        if len(tickers_bse) != 0 and tickers_bse[0] != "":
            for ticker in tickers_bse:
                ticker_BO = ticker + ".BO"
                self.RSI(ticker_BO, self.Dict, ticker)
                self.plot_divergence(ticker_BO, self.Dict)


    

    def analyze_stocks(self):
        file_name = self.entry.get()
        if not file_name:
            messagebox.showwarning("Warning", "Please enter a file name!")
            return
        self.Dict = {}
        self.STOCKS(file_name)

        buy = []
        sell = []
        hold = []
        nothold = []

        self.Dict = dict(sorted(self.Dict.items(), reverse=True, key=lambda item: item[1][0]))

        for key, value in self.Dict.items():
            if (value[0] >= 67.5) and ((value[0] < value[1] < value[2]) or (value[0] < value[2])):
                sell.append(f"{key} : {value[0]}")

            elif (value[0] <= 33.5) and ((value[0] > value[1] > value[2]) or (value[0] > value[2])):
                buy.append(f"{key} : {value[0]}")

            elif ((value[0] < value[1] < value[2] < value[3] < value[4]) or
                  (value[0] < value[1] < value[2] < value[3]) or
                  (value[0] < value[1] < value[2]) or
                  (value[0] < value[1] < value[2] < value[4]) or
                  (value[0] < value[1] < value[3] < value[4]) or
                  (value[0] < value[2] < value[3] < value[4]) or
                  (value[1] < value[2] < value[3] < value[4]) or
                  (value[0] < value[1] < value[3]) or
                  (value[0] < value[2] < value[3]) or
                  (value[0] < value[3] < value[4]) or
                  (value[0] < value[1] < value[4])):
                nothold.append(f"{key} : {value[0]}")

            else:
                hold.append(f"{key} : {value[0]}")

        if len(buy) > 1:
            buy.reverse()

        length = [len(buy), len(sell), len(hold), len(nothold)]
        max_length = max(length)

        buy.extend([" "] * (max_length - len(buy)))
        sell.extend([" "] * (max_length - len(sell)))
        hold.extend([" "] * (max_length - len(hold)))
        nothold.extend([" "] * (max_length - len(nothold)))

        stocks = {
            "    BUY         ": buy,
            "    SELL        ": sell,
            "    HOLD        ": hold,
            "    DOWN        ": nothold
        }

        stocks_df = pd.DataFrame(stocks)
        table = stocks_df.to_string()

        with open("Table.txt", "w") as file:
            file.write(table)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, table)
        messagebox.showinfo("Analysis Complete", "Analysis completed successfully. Results written to Table.txt.")

     

root = tk.Tk()
app = StockAnalyzerApp(root)
root.mainloop()
