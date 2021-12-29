import logging
import time

from algosdk.future import transaction
from algosdk.transaction import AssetTransferTxn

from accountSetUp import jointAuthorization, account_sk
from connection import algo_client
from connection import params
from printAssetHolding import print_asset_holding
from waitForConfirmation import wait_for_confirmation
from getAssetId import getAssetIdv2
from accountSetUp import asset_revocation_authorized, transaction_executor, account_sk


# The asset_revocation_authorized Account revokes ISA from target_Account 'x' and forward to transaction_executor account.
# Specify fee and flat-fee parameters instead of network suggested parameters
def assetRevocation(amount, target_account):
    params.fee = 1000
    params.flat_fee = True
    asset_id = getAssetIdv2(transaction_executor)
    # Must be signed by the account that is the Asset's authorized clawback account
    txn = AssetTransferTxn(
        sender=asset_revocation_authorized,
        sp=params,
        receiver=transaction_executor,
        amt=amount,
        index=asset_id,
        revocation_target=target_account
    )
    join_Sig = jointAuthorization()[1]

    # Effect clawback by complete approval from required accounts
    jointTrxn = transaction.MultisigTransaction(txn, join_Sig)
    jointTrxn.sign(account_sk[0])  # Required account 1 signs the transaction
    jointTrxn.sign(account_sk[1])  # Required account 2 signs the transaction
    jointTrxn.sign(account_sk[2])  # Required account 3 signs the transaction

    # Submit transaction to the network
    tx_id = algo_client.send_transaction(jointTrxn, headers={'content-type': 'application/x-binary'})
    message = "Transaction was signed with: {}.".format(tx_id)
    wait = wait_for_confirmation(tx_id)
    time.sleep(2)
    isRevoked = bool(wait is not None)
    print(isRevoked)
    # Now check the asset holding for target account.
    # This should now show a holding with 0 balance.
    assetHolding = print_asset_holding(target_account, asset_id)
    logging.info(
        "...##Asset Transfer... \nTarget account: {}.\nMessage: {}\nOperation: {}\nHoldings: {}\n".format(
            target_account,
            message,
            assetRevocation.__name__,
            assetHolding
        ))
    print("Receiver of revoked asset: ")
    print_asset_holding(algo_client, target_account, asset_id)

    # The balance of account 1 should increase by 10 to 1000.
    print("Account 1")
    print_asset_holding(algo_client, transaction_executor, asset_id)
