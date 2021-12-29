from connection import algo_client


# Searches and returns an asset Id
def getAssetIdv2(sourceAddr):
    # Get account info of asset creator
    account_info = algo_client.account_info(sourceAddr)
    _Id = account_info["assets"][0]["asset-id"]
    return _Id
