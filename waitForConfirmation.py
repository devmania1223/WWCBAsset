from connection import Connect
import logging

# Establish a connection
connect = Connect()
algo_client = connect.connectToNetwork()


def wait_for_confirmation(txid):
    """Utility function to wait until the transaction is
    confirmed before proceeding."""
    last_round = algo_client.status().get('last-round')
    txinfo = algo_client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        wait = "Waiting for confirmation..."
        last_round += 1
        status = algo_client.status_after_block(last_round)
        txinfo = algo_client.pending_transaction_info(txid)
        logging.info("..@dev wait for confirmation.. \nStatus: {}\nTransaction {} confirmed in round {}\nTxn Info: {}\nResponse: {}".format(
        status,
        txid,
        txinfo.get('confirmed-round'),
        txinfo,
        wait
        ))
    return txinfo