from connection import algo_client, params
from accountSetUp import account_sk, asset_manage_authorized, jointAuthorization
from printAssetHolding import print_asset_holding
from waitForConfirmation import wait_for_confirmation
from algosdk.future.transaction import AssetTransferTxn, transaction
# import time
import logging


def transferISA(rec, amount):
    params.fee = 1000
    params.flat_fee = True
    assetId = 10684835

    txn = AssetTransferTxn(
        sender=asset_manage_authorized,
        sp=params,
        receiver=rec,
        amt=amount,
        index=assetId
    )
    # Sign the transaction
    jointSig = jointAuthorization()[1]

    # Effect clawback by complete approval from required accounts
    jointTrxn = transaction.MultisigTransaction(txn, jointSig)
    jointTrxn.sign(account_sk[0])  # Required account 1 signs the transaction
    jointTrxn.sign(account_sk[1])  # Required account 2 signs the transaction
    jointTrxn.sign(account_sk[2])  # Required account 3 signs the transaction

    # Submit transaction to the network
    tx_id = algo_client.send_transaction(jointTrxn, headers={'content-type': 'application/x-binary'})
    message = "Transaction was signed with: {}.".format(tx_id)
    wait = wait_for_confirmation(tx_id)
    isSuccessful = bool(wait is not None)
    print(isSuccessful)
    # Now check the asset holding for receiver.
    # This should now show a holding with the sent balance.
    assetHolding = print_asset_holding(rec, assetId)
    logging.info(
        "...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\nHoldings: {}\n".format(
            rec,
            message,
            transferISA.__name__,
            assetHolding
        ))


transferISA("WPFWHLPNY6HLTDGSMMC7O3LTWHEEFS234KN2AML6KXKWXUQSMNZSK5C6VU", 50000)
