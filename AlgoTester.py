from Coin import Coin
import json
from binance.client import Client


class AlgoTester:
    test_secrets_path = "./secrets/test_secrets.json"
    real_secrets_path = "./secrets/secrets.json"

    def __init__(self, testrun=True):
        secrets_path = self.test_secrets_path if testrun else self.real_secrets_path
        secrets_file = open(secrets_path)
        secrets = json.load(secrets_file)
        self.client = Client(secrets["api_key"], secrets["api_secret"])
        if testrun:
            self.client.API_URL = 'https://testnet.binance.vision/api'

        exchange_info = self.client.get_exchange_info()
        for s in exchange_info['symbols']:
            print(s['symbol'])

        self.coin = Coin(coin_symbol='BTC', fiat_symbol='EUR', client=self.client, resources=50)

    def testRun(self, low, high, interval, indicator):
        start_money = 1000
        money = start_money
        amount = 0
        self.coin.getData(interval=interval, time_range='1 Years ago UTC')
        low_ind = indicator + str(low)
        high_ind = indicator + str(high)
        price = self.coin.data_frame['price']
        self.coin.calculateIndicator(length=low, indicator='ema')
        self.coin.calculateIndicator(length=high, indicator='ema')
        for i in range(high + 2, len(price)):
            if amount > 0:
                if self.coin.data_frame[low_ind][i - 2] >= self.coin.data_frame[high_ind][i - 2]:
                    if self.coin.data_frame[low_ind][i - 1] < self.coin.data_frame[high_ind][i - 1]:
                        money = amount * price[i]
                        amount = 0
            else:
                if self.coin.data_frame[low_ind][i - 2] <= self.coin.data_frame[high_ind][i - 2]:
                    if self.coin.data_frame[low_ind][i - 1] > self.coin.data_frame[high_ind][i - 1]:
                        amount = money / price[i]
                        money = 0
        if money == 0:
            money = amount * price[-1]
        return money

    def simplyAlgoTest(self):
        intervals = ['15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d']
        intervals.reverse()
        results = []
        indicators = ['ema']
        for indicator in indicators:
            for interval in intervals:
                for low in range(10, 51, 10):
                    for high in range(3, 11):
                        print("testing algo: low:{} high:{} interval:{} indicator:{}".format(low, int(high / 2 * low),
                                                                                             interval,
                                                                                             indicator))
                        result = [low, high, interval, indicator,
                                  self.testRun(low, int(high / 2 * low), interval, indicator)]
                        print("results: {}/{}".format(result[4], 1000))
                        results.append(result)

        print(results)
        best_result = [0, 0, 0, 0, 0]
        for result in results:
            if result[4] > best_result[4]:
                best_result = result

        print("best result is: {}".format(best_result))

    def macdTester(self):
        intervals = ['15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
        intervals.reverse()
        results = []
        for interval in intervals:
            self.coin.getData(interval=interval, time_range='1 Year ago UTC')
            for fast in range(10, 31):
                for slow in range(2, fast + 31):
                    for signal in range(3, 20):
                        result = [fast, slow, signal, interval, self.macdTest(fast=fast, slow=slow, signal=signal)]
                        print(result)
                        results.append(result)

        print(results)
        best_result = [0, 0, 0, 0, 0]
        for result in results:
            if result[4] > best_result[4]:
                best_result = result
        print("best result is: {}".format(best_result))

    def macdTest(self, fast, slow, signal):
        self.coin.getData(interval='15m', time_range='3 Days ago UTC')
        self.coin.calculateMacd(fast=fast, slow=slow, signal=signal)
        macd = self.coin.macd.macd()
        macd_signal = self.coin.macd.macd_signal()
        dates = self.coin.dates
        money = 1000
        amount = 0
        for i in range(slow + signal, len(macd) - 2):
            if amount > 0:
                if macd[i - 2] >= macd_signal[i - 2] and macd[i - 1] < macd_signal[i - 1]:
                    money = amount * self.coin.close_prices[i]
                    amount = 0
            else:
                if macd[i - 2] <= macd_signal[i - 2] and macd[i - 1] > macd_signal[i - 1]:
                    amount = money / self.coin.close_prices[i]
                    money = 0
        if amount > 0:
            money = amount * self.coin.close_prices.values[-1]
        return money


if __name__ == "__main__":
    cos = AlgoTester(testrun=False)
    print(cos.macdTest(11, 2, 3))
    #cos.macdTester()
