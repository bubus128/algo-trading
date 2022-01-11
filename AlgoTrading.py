import json
from binance.client import Client
from Coin import Coin

testrun = False


class AlgoTrading:
    test_secrets_path = "./secrets/test_secrets.json"
    real_secrets_path = "./secrets/secrets.json"

    def __init__(self):
        secrets_path = self.test_secrets_path if testrun else self.real_secrets_path
        secrets_file = open(secrets_path)
        secrets = json.load(secrets_file)
        self.client = Client(secrets["api_key"], secrets["api_secret"])
        if testrun:
            self.client.API_URL = 'https://testnet.binance.vision/api'

        exchange_info = self.client.get_exchange_info()
        for s in exchange_info['symbols']:
            print(s['symbol'])

        bitcoin = Coin(symbol='BTCEUR', client=self.client, cost=50)
        bitcoin.simpleAlgo()


if __name__ == "__main__":
    cos = AlgoTrading()
