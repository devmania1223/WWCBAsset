from connection import algo_client
import logging
import json


# Prints asset Holding of an account
def print_created_asset(bankAddr, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = algo_client.account_info(bankAddr)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1
        if scrutinized_asset['index'] == assetid:
            asset_id = scrutinized_asset['index']
            data_json = json.dumps(my_account_info['params'], indent=4)
            logging.info("...##Asset holding... \nAddress: {}.\n Asset ID: {}\nData in Json: {}\nOperation: {}\n".format(
                bankAddr,
                asset_id,
                data_json,
                print_created_asset.__name__
                ))
            return data_json
        else:
            active = False
            return "Asset does not exist"