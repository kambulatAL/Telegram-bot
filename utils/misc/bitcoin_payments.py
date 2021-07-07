import decimal
from datetime import datetime

import blockcypher
from dateutil.tz import tzutc

from data import config


class AddressDetails:
    def __init__(self, address: str, total_received: int, total_sent: int, balance: int,
                 unconfirmed_balance: int, unconfirmed_txrefs: list, txrefs: list,
                 **kwargs):
        self.address = address
        self.total_received = total_received
        self.total_sent = total_sent
        self.balance = balance
        self.unconfirmed_balance = unconfirmed_balance
        self.unconfirmed_txrefs = unconfirmed_txrefs
        self.txrefs = txrefs


class NotConfirmed(Exception):
    pass


class NoPaymentFound(Exception):
    pass


class Payment:
    def __init__(self, amount: decimal):
        self.amount = amount

    def create(self):
        self.created = datetime.now(tz=tzutc())

    def check_payments(self):
        details = blockcypher.get_address_details(address=config.BTC_WALLET,
                                                  api_key=config.BLOCKCYPHER_TOKEN)
        address_details = AddressDetails(**details)

        for transaction in address_details.unconfirmed_txrefs:
            if transaction.get('value') == self.amount:
                if transaction.get('received') >= self.created:
                    if transaction.get('confirmations') > 0:
                        return True
                    else:
                        raise NotConfirmed

        for transaction in address_details.unconfirmed_txrefs:
            if transaction.get('value') == self.amount:
                if transaction.get('received') >= self.created:
                    return True
        raise NoPaymentFound
