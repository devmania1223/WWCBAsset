from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, account
from getAssetId import getAssetIdv2
from connection import algo_client, params
from algosdk import mnemonic
from waitForConfirmation import wait_for_confirmation
import time
from printAssetHolding import print_asset_holding
from printCreatedAsset import print_created_asset
from accountSetUp import *
import logging
from clawback import assetRevocation

logging.basicConfig(filename='{}.log'.format("draftfile"), level=logging.INFO)


# Create an Bankers asset
def create_ISA():
    # suggest parameters rather than using network's
    params.fee = 1000
    params.flat_fee = True

    # Asset Creation transaction
    # Assigns transaction fields.
    txn = AssetConfigTxn(
        sender=transaction_executor,  # MultiSig account. Requires 4 signatures to create an asset
        sp=params,
        total=70000000,
        default_frozen=False,  # Asset will not be frozen by default. It has be explicit
        unit_name="ISA",  # Such as cent is to Dollar and kobo is to Naira
        asset_name="CBDC-Asset-1",
        manager=asset_manage_authorized,
        reserve=asset_reserve_based,
        freeze=asset_freeze_authorized,
        clawback=asset_revocation_authorized,
        url="http//algorand.com/asa/",
        strict_empty_address_check=True,  # Setting this to true prevents accidental removal of admin access to asset or deleting the asset
        decimals=0
    )

    _join_Sig = jointAuthorization()
    _jointSig = _join_Sig[1]

    _sig = transaction.MultisigTransaction(txn, _jointSig)
    # Effect clawback by completely extract approval from required accounts
    _sig.sign(account_sk[0])  # Required account 1 signs the transaction
    _sig.sign(account_sk[1])  # Required account 2 signs the transaction
    _sig.sign(account_sk[2])  # Required account 3 signs the transaction
    # joint_Sig = transaction.MultisigTransaction

    # Send the transaction to the network and retrieve the txid.
    txnReference = algo_client.send_transaction(_sig, headers={'content-type': 'application/x-binary'})

    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.

    # Wait for the transaction to be confirmed
    confirmation = wait_for_confirmation(txnReference)
    time.sleep(2)
    try:
        # Pull account info of the creator
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = algo_client.pending_transaction_info(txnReference)
        asset_id = ptx["asset-index"]
        createdBankerAsset = print_created_asset(transaction_executor, asset_id)
        assetHolding = print_asset_holding(transaction_executor, asset_id)
        logging.info(
            "...@dev/created Asset WIN... \nSource Address: {}\nOperation 1 : {}\nOperation 2: {}\nOperation 3: {}\nAsset ID: {}\nCreated Asset: {} \nAsset Holding: {}\nWait for confirmation\n".format(
                transaction_executor,
                create_ISA().__name__,
                print_created_asset.__name__,
                print_asset_holding.__name__,
                asset_id,
                createdBankerAsset,
                assetHolding,
                confirmation
            ))
    except Exception as err:
        print(err)


# Execute Asset creation
# create_ISA()


# Database <Leaf Banks>
class LeafBanks:
    def __init__(self, bankName, *others):
        self.bankName = bankName
        self.leafList = [].append(self.bankName)
        self.others = others
        pass


# Modelling Leaf Banks to opting for Bankers' asset
class Bankers(LeafBanks):
    def __init__(self, bankName, *others):
        super().__init__(bankName, *others)
        self.accruals = "debt"
        self.members = []
        self.resolved = []
        self.hasResolve = False
        self.refNumber = ["GT-13004"]
        self.clearance = None

    # Member Banks to opt in for Bankers' asset
    def resolve(self, bankrIdentifier, skey):
        # Check if Leafbank holding Bankers' asset prior to opt-in
        assetId = getAssetIdv2(transaction_executor)
        account_info_pk = algo_client.account_info(bankrIdentifier)
        holding = None
        idx = 0
        print(account_info_pk)
        for assetinfo in account_info_pk['assets']:
            scrutinized_asset = assetinfo[idx]
            idx = idx + 1
            if assetId == scrutinized_asset['asset-id']:
                holding = True
                msg = "This address has opted in for ISA, ID {}".format(assetId)
                logging.info("Message: {}".format(msg))
                logging.captureWarnings(True)
                break
        if not holding:
            # Use the AssetTransferTxn class to transfer assets and opt-in
            txn = AssetTransferTxn(
                sender=bankrIdentifier,
                sp=params,
                receiver=bankrIdentifier,
                amt=0,
                index=assetId
            )
            # Sign the transaction
            # Firstly, convert mnemonics to private key--.
            sk = mnemonic.to_private_key(seed)
            sendTrxn = txn.sign(sk)

            # Submit transaction to the network
            txid = algo_client.send_transaction(sendTrxn, headers={'content-type': 'application/x-binary'})
            message = "Transaction was signed with: {}.".format(txid)
            wait = wait_for_confirmation(txid)
            time.sleep(2)
            hasOptedIn = bool(wait is not None)
            if hasOptedIn:
                self.hasResolve = True
                print(assetId)
            # Now check the asset holding for that account.
            # This should now show a holding with 0 balance.
            assetHolding = print_asset_holding(bankrIdentifier, assetId)
            logging.info("...##Asset Transfer... \nLeaf Bank address: {}.\nMessage: {}\nHas Opted in: {}\nOperation: {}\nHoldings: {}\n".format(
                    bankrIdentifier,
                    message,
                    hasOptedIn,
                    Bankers.resolve.__name__,
                    assetHolding
                ))
            return hasOptedIn

    # User is required to create account First to proceed further
    def generateBankerAddr(self, ref_number):
        if ref_number in self.refNumber:
            sk, accountIdentifier = account.generate_account()
            seedPhrase = mnemonic.from_private_key(sk)
            self.members.append(accountIdentifier)  # Remembers bankers identifier
            return (seedPhrase, accountIdentifier)
        else:
            print("You're not recognized")

    # On compliance with certain rules, a leaf bank is opted in
    def canResolve(self, account_id, refNumber, name, sk):
        accountid = bool(account_id in self.members)
        while accountid:
            if account_id in self.members:
                self.clearance = 'cleared'
                if (self.clearance is not None) and (account_id in self.members) and (refNumber not in self.resolved):
                    self.accruals = None
                    g = Bankers(name)
                    g.resolve(account_id, sk)
                    self.hasResolve = True
                    self.resolved.append(refNumber)
                    print("Resolved\nPlease proceed to the next action.")
                break


i = Bankers("Guarantee Trust Bank", "Lagos", "Marina", "Nigeria")
seed, pk = i.generateBankerAddr("GT-13004")  # Get mnemonics and public key
print(seed, pk)

time.sleep(50)  # Wait time to fund account leaf bank for transaction fee
i.canResolve(pk, "GT-13004", "Guarantee Trust Bank", seed)

