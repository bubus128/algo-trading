import json
from binance.client import Client

testrun = True


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
        print(self.client.get_asset_balance(asset='BNB'))


if __name__ == "__main__":
    cos = AlgoTrading()
