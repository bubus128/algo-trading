import json
import time
import _thread
from binance.client import Client
from Coin import Coin


class AlgoTrading:
    test_secrets_path = "./secrets/test_secrets.json"
    real_secrets_path = "./secrets/secrets.jsonn"

    def __init__(self, testrun=True, currency='EUR', resources=30, approved_coins=None):
        self.operating_symbols = []
        self.coins = []
        secrets_path = self.test_secrets_path if testrun else self.real_secrets_path
        secrets_file = open(secrets_path)
        secrets = json.load(secrets_file)
        self.client = Client(secrets["api_key"], secrets["api_secret"])
        if testrun:
            self.client.API_URL = 'https://testnet.binance.vision/api'


        exchange_info = self.client.get_exchange_info()
        for symbol in exchange_info['symbols']:
            if symbol['quoteAsset'] == currency and 'MARKET' in symbol['orderTypes']:
                if approved_coins is None or symbol['baseAsset'] in approved_coins:
                    coin = Coin(coin_symbol=symbol['baseAsset'], fiat_symbol=symbol['quoteAsset'], client=self.client,
                                resources=resources)
                    self.coins.append(coin)
        '''
        for coin in self.coins:
            try:
                _thread.start_new_thread(self.simpleEma, (coin, ))
            except:
                print("Error: unable to start thread")
        '''

    def macdTrade(self, coin, interval='6h', fast=12, slow=19, signal=9):
        while True:
            coin.getData(interval=interval, time_range='45 Days ago UTC')
            coin.calculateMacd(fast=fast, slow=slow, signal=signal)
            macd = coin.macd.macd().values
            macd_signal = coin.macd.macd_signal().values
            if coin.amount > 0:
                if macd[-2] >= macd_signal[-2] and macd[-1] < macd_signal[-1]:
                    coin.sell()
            else:
                if macd[-2] <= macd_signal[-2] and macd[-1] > macd_signal[-1]:
                    coin.buy()
            print(coin)
            time.sleep(6*3600)

    def simpleEma(self, coin):
        while True:
            coin.getData(interval='12h', time_range='45 Days ago UTC')
            ema20 = coin.calculateIndicator(length=20, indicator='ema')
            ema40 = coin.calculateIndicator(length=40, indicator='ema')
            if coin.amount > 0:
                if ema20[-2] >= ema40[-2]:
                    if ema20[-1] < ema40[-1]:
                        coin.sell()
            else:
                if ema20[-2] <= ema40[-2]:
                    if ema20[-1] > ema40[-1]:
                        coin.buy()


if __name__ == "__main__":
    cos = AlgoTrading(testrun=False, approved_coins=['BNB'])
