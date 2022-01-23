import time

from ta.trend import *
from ta.momentum import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime


class Coin:
    def __init__(self, coin_symbol, fiat_symbol, client, resources, min_amount=0):
        self.macd = None
        self.close_prices = None
        self.state = None
        self.dates = None
        self.start_resources = resources
        self.resources = resources
        self.amount = 0
        self.value = 0
        self.client = client
        self.symbol = coin_symbol + fiat_symbol
        self.coin_symbol = coin_symbol
        self.fiat_symbol = fiat_symbol
        self.info = client.get_symbol_info(self.symbol)
        self.min_amount = min_amount
        filters = self.info['filters']
        for filter in filters:
            if filter['filterType'] == 'LOT_SIZE':
                self.sell_step = filter['stepSize']

    def reset(self):
        self.amount = 0
        self.resources = self.start_resources

    def getData(self, interval='1h', time_range='1 week ago UTC'):
        bars = None
        while 1:
            try:
                bars = self.client.get_historical_klines(self.symbol, interval, time_range)
                break
            except:
                continue

        self.dates = [datetime.fromtimestamp(row[0] / 1000) for row in bars]
        self.close_prices = pd.Series(list(map(float, [row[4] for row in bars])))

    def calculateMacd(self, fast, slow, signal):
        self.macd = MACD(close=self.close_prices, window_fast=fast, window_slow=slow, window_sign=signal)

    def calculateIndicator(self, length, indicator='ema', startpoint=None):
        name = ''
        if indicator == 'ema':
            name = 'ema' + str(length)
            if startpoint is not None:
                close_prices = self.data_frame['close'][0:startpoint+1]
            else:
                close_prices = self.data_frame['close']
            self.data_frame[name] = EMAIndicator(close=close_prices, window=length)

        if indicator == 'rsi':
            name = "rsi" + str(length)
            self.data_frame[name] = RSIIndicator(close=self.data_frame['close'], window=length)

        return list(self.data_frame[name])

    def sell(self):
        try:
            amount = float(self.client.get_asset_balance(asset=self.coin_symbol)['free']) - self.min_amount
            amount = amount - (amount % self.sell_step)
            sell_order = self.client.create_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=amount)
            if sell_order['status'] == 'FILLED':
                self.amount = float(self.client.get_asset_balance(asset=self.coin_symbol)['free']) - self.min_amount
                self.resources += float(sell_order['cummulativeQuoteQty'])
                return self.resources
            else:
                return 0
        except BinanceAPIException as e:
            print(e)
        except BinanceOrderException as e:
            print(e)

    def buy(self):
        try:
            buy_order = self.client.create_order(symbol=self.symbol, side='BUY', type='MARKET',
                                                 quoteOrderQty=self.resources)
            if buy_order['status'] == 'FILLED':
                self.amount = float(self.client.get_asset_balance(asset=self.coin_symbol)['free']) - self.min_amount
                self.resources -= float(buy_order['cummulativeQuoteQty'])
                return self.amount
            else:
                return 0
        except BinanceAPIException as e:
            print(e)
        except BinanceOrderException as e:
            print(e)

    def __str__(self):
        approximate_value = self.amount*self.close_prices.values[-1]
        profit = ((approximate_value + self.resources) / self.start_resources - 1) * 100
        print_str = 'resources: {}€ \namount: {}{} ({}€)\n profit: {}%'.\
            format(self.resources, self.amount, self.coin_symbol, approximate_value, profit)
        return print_str
