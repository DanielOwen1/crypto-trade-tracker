from contextlib import contextmanager

from binance import Client
from binance.exceptions import BinanceAPIException
from django.conf import settings


INVALID_SYMBOL = -1121

INITIAL_BASE_ASSETS = [
    'BTC', 'ETH', 'LTC', 'BNB', 'ADA', 'BAKE', 'CAKE', 'GAS', 'NEO', 'GRT', 'VET', 'NANO', 'MATIC'
]

INITIAL_QUOTE_ASSETS = [
    'GBP', 'USDT', 'BTC', 'ETH', 'BNB', 'EUR', 'BUSD'
]

INITIAL_PAIRS = [
    '%s%s' % (base_asset, quote_asset) for base_asset in INITIAL_BASE_ASSETS for quote_asset in INITIAL_QUOTE_ASSETS
]


@contextmanager
def catch_binance_error(*error_codes):
    try:
        yield
    except BinanceAPIException as e:
        if e.code not in error_codes:
            raise


def client():
    return Client(settings.BINANCE_API_KEY, settings.BINANCE_SECRET_KEY)


def get_all_orders(symbol):
    return client().get_all_orders(symbol=symbol)


def fetch_symbol_price_if_exists(symbol):
    with catch_binance_error(INVALID_SYMBOL):
        return client().get_avg_price(symbol=symbol)

