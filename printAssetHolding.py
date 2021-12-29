from connection import algo_client
import logging
import json


# Utility function used to print asset holding for account and assetid
def print_asset_holding(accountAddr, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algo_client.account_info(accountAddr)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if scrutinized_asset['asset-id'] == assetid:
            asset_id = scrutinized_asset['asset-id']
            data_json = json.dumps(scrutinized_asset, indent=4)
            logging.info("...##Asset holding... \nAddress: {}.\n Asset ID: {}\nData in Json: {}\nOperation: {}\n".format(
                accountAddr,
                asset_id,
                data_json,
                print_asset_holding.__name__
                ))
            return data_json
        else:
            active = False
            return "You do not own any of the Bank's asset"
