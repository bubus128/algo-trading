import time

from binance.client import Client
import pandas as pd
import pandas_ta as ta
from plotnine import *
from datetime import datetime


class Coin:
    def __init__(self, symbol, client, cost):
        self.data_frame = None
        self.state = None
        self.cost = cost
        self.amount = 0
        self.value = 0
        self.client = client
        self.symbol = symbol

    def getData(self, interval='15min', time_range='1 week ago UTC'):
        bars = self.client.get_historical_klines(self.symbol, interval, time_range)
        for line in bars:
            del line[5:]
            # Changing close price type to float
            line[4] = float(line[4])
            # Conversion from server time to data time
            line[0] = datetime.fromtimestamp(line[0]/1000)
        self.data_frame = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
        self.data_frame['price'] = self.data_frame['close'].tolist()

    def calculateEMA(self, length):
        name = 'ema' + str(length)
        self.data_frame[name] = ta.ema(self.data_frame['close'], length=length)

    def calculateSMA(self, length):
        name = 'sma' + str(length)
        self.data_frame[name] = ta.sma(self.data_frame['close'], length=length)

    def calculateRSI(self, length):
        name = "rsi" + str(length)
        self.data_frame[name] = ta.rsi(self.data_frame['close'], length=length)

    def calculateIndicators(self):
        self.calculateSMA(length=20)
        self.calculateSMA(length=100)
        self.calculateRSI(length=14)
        self.calculateEMA(length=20)
        self.calculateEMA(length=100)

    def graph(self):
        plot = ggplot(self.data_frame, aes(x='date')) \
               + geom_line(aes(y='ema20'), color='green') \
               + geom_line(aes(y='ema100'), color='red') \
               + geom_line(aes(y='price'), color='blue')
        print(plot)

    def simpleAlgo(self):
        while 1:
            self.getData(interval='15m', time_range='1 week ago UTC')
            self.calculateIndicators()
            self.graph()
            time.sleep(3)
