from binance.client import Client
import btalib
import pandas as pd


class Coin:
    def __init__(self, symbol, client):
        self.data_frame = None
        self.client = client
        self.symbol = symbol

    def getData(self, interval='1h', time='1 week ago UTC'):
        bars = self.client.get_historical_klines(self.symbol, interval, time)
        for line in bars:
            del line[5:]
        self.data_frame = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])

    def calculateEMA(self, interval):
        pass

    def calculateSMA(self, interval):
        name = 'sma' + str(interval)
        self.data_frame[name] = btalib.sma(self.data_frame.close, period=interval).df

    def simpleAlgo(self):
        self.getData(interval='1h', time='1 week ago UTC')
        self.calculateSMA(interval=20)
        self.calculateSMA(interval=100)
