import logging
from algosdk import transaction
from algosdk import mnemonic

logging.basicConfig(filename='{}.log'.format("draftfile"), level=logging.INFO)

# Firstly, generate 5 accounts - it returns 5 public keys with 6 secret keys
# For testing, we are accessing Member of join authorization's secret key. Meanwhile, in production,
# We would not want to have the knowledge of the keys
# Get mnemonic words if using goal or rather use the acount.generate_account() to generate accounts if using API service
seed1 = "odor cash burst duck imitate gesture peasant raw deliver moral become butter right weekend then admit matter cube invest current bridge afford filter abandon trial"
seed2 = "cabin invite legend involve thank indicate decline wide resist gas nuclear wedding only prepare time hand mistake produce devote trash fly bamboo balcony able brass"
seed3 = "general turkey veteran purity sad please omit trust penalty toilet exclude tool desert service float like rabbit sand gesture potato black such muffin absent admit"
seed4 = "coconut remind assist invite hat figure smoke extra style blind burger tattoo hub pencil slot sorry region youth hip hover veteran crisp uniform absent annual"
seed5 = "climb minimum keep power replace farm genre swarm broken layer rather confirm ritual awesome glory retire stay room unfair sausage cup outdoor pair abstract employ"

# Get public addresses and secret keys from mnemonics
mnemonics = [seed1, seed2, seed3, seed4, seed5]
accounts = {}
counter = 1
for seed in mnemonics:
    accounts['account{}_pk'.format(counter)] = [mnemonic.to_public_key(seed)]
    accounts['account{}_sk'.format(counter)] = [mnemonic.to_private_key(seed)]
    counter += 1

account1_pk = accounts['account1_pk'][0]
account2_pk = accounts['account2_pk'][0]
account3_pk = accounts['account3_pk'][0]
account4_pk = accounts['account4_pk'][0]
account5_pk = accounts['account5_pk'][0]

logging.info(
            "..@dev Accounts in ISA.. \naccount1_pk: {}\naccount2_pk: {}\naccount3_pk: {}account4_pk: {}\n".format(
                account1_pk,
                account2_pk,
                account3_pk,
                account4_pk
            ))

# Secret keys (For demonstration purpose only)
account_sk = [
    accounts['account1_sk'][0],
    accounts['account2_sk'][0],
    accounts['account3_sk'][0],
    accounts['account4_sk'][0],
    accounts['account5_sk'][0]
]
# Collect generated public keys
addressList = [account1_pk, account2_pk, account3_pk, account4_pk]

asset_role = [
    "Manage",
    "Reserve",
    "Freezer",
    "Revocation",
    "Trxn_executor"
]


# Extract account from joint authorization i.e Signed transaction using MultiSig class
def jointAuthorization():
    version = 1
    required_jointThreshold = 3
    err = "{}\n{}".format(
        "Authorization count should equal to number of addresses",
        "More than one account is needed to create join authorization",
        "Version as at now cannot be greater or less than 1"
    )
    # jointSig represents and mimics a transaction that was approved by the required signatures
    # but actually incomplete until they ratify or jointly reach a consensus
    try:
        # returns Multisig object without signature
        joinAuths = transaction.Multisig(version, required_jointThreshold, [account1_pk, account2_pk, account3_pk])
        # jointSig = transaction.MultisigTransaction
        jointAddr = joinAuths.address()  # return a Multi-Signature address
        logging.info(
            "..@dev created multi-Signature accounts.. \nOperation: {}\nJoint Address: {}\nAddresses supplied: {}\n".format(
                jointAuthorization.__name__,
                jointAddr,
                [account1_pk, account2_pk, account3_pk],
            ))
        return jointAddr, joinAuths
    except Exception as e:
        print(e, err)


# Generate multisig accounts for all four roles
def generateAuthorizationAccounts():
    _authorized = {}
    if len(addressList) == 4:
        jointApprAccount = jointAuthorization()
        for role in asset_role:
            _authorized[role] = jointApprAccount[0]
        logging.info(
            "..@dev Generate Authorization Accounts.. \nOperation: {}\nJoint Address: {}\n".format(
                generateAuthorizationAccounts.__name__,
                _authorized,
            ))
        return _authorized
    else:
        return "Addresses surpass asset roles"


authorized = generateAuthorizationAccounts()
print(authorized)

# Role-based addresses produced from multiSig account.
# Note that we need them ahead to include in asset configuration transaction fields.
# For instance, if asset_freeze_authorized is set to the return value of generateAuthorizationAccounts, for asset to be revoked,
# secret keys equivalent to required_jointThreshold i.e 4 addresses involved must be supplied for transaction to be valid
asset_manage_authorized = authorized["Manage"]  # Account authorised to update asset's configuration
asset_reserve_based = authorized["Reserve"]  # Account authorized to mint/release asset into circulation
asset_freeze_authorized = authorized["Freezer"]  # Account licensed to freeze asset in holder's address
asset_revocation_authorized = authorized["Revocation"]  # Account authorized to take asset from any account

# Operational/Asset creator address
transaction_executor = authorized["Trxn_executor"]  # Fund this account to execute transaction
account_executor_auth = authorized["Freezer"]  # Secret key of operational account i.e account

# Log output to file
logging.info(
    "..@dev created multi-Signature accounts.. \nOperation: {}\nasset_manage_authorized: {}\nasset_reserve_based: {}\nasset_freeze_authorized: {}\nasset_revocation_authorized: {}\nTransaction_executor: {}\n".format(
        "Role-based Accounts",
        asset_manage_authorized,
        asset_reserve_based,
        asset_freeze_authorized,
        asset_revocation_authorized,
        transaction_executor
    ))