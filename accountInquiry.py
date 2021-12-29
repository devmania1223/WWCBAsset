from connection import algo_client
import logging


# Get account information of an address
def enquireAddress(accountAddress):
    try:
        assert(len(accountAddress) == 58)
        account_info = algo_client.account_info(accountAddress)
        print(account_info)
        logging.info("..@dev Enquire account.. \nAccount information: {}\n".format(account_info))
    except Exception as err:
        msg = "Address is invalid. \n Length must be 58\n"
        logging.info("..@dev Enquire account Error.. \nError getting account information: {}Message: {}\n".format(msg, err))
