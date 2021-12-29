from algosdk.v2client import algod
import os


# Setup HTTP client w/guest key provided by PureStake
class Connect:
    def __init__(self):
        # declaring the third party API
        self.algod_address = os.environ.get('PURESTAKE_URL')
        # <-----shortened - my personal API token
        self.algod_token = os.environ.get('PERSONAL_API_TOKEN_PURESTAKE')
        self.headers = {"X-API-Key": self.algod_token}

    def connectToNetwork(self):
        # establish connection
        return algod.AlgodClient(self.algod_token, self.algod_address, self.headers)


connect = Connect()
algo_client = connect.connectToNetwork()
params = algo_client.suggested_params()