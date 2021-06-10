from binance import Client
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from core import binance_client


class RelevantSpotOrder(models.Manager):
    def get_queryset(self):
        return super(RelevantSpotOrder, self).get_queryset().exclude(
            Q(symbol__icontains='UP') |
            Q(symbol__icontains='DOWN') |
            Q(symbol__icontains='BUll') |
            Q(symbol__icontains='BEAR')
        )


class Symbol(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(decimal_places=8, max_digits=18, blank=True, null=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    relevant = RelevantSpotOrder()

    def clean(self):
        if binance_client.fetch_symbol_price_if_exists(self.symbol) is None:
            raise ValidationError('%s is an invalid symbol' % self.symbol)

    @staticmethod
    def import_from_binance(*extra_base_assets):
        symbols_to_fetch = list(set(binance_client.INITIAL_BASE_ASSETS) | set(map(str.upper, extra_base_assets)))
        all_coins = binance_client.client().get_all_tickers()
        Symbol.objects.bulk_create(
            (Symbol(**symbol_info) for symbol_info in all_coins if any(
                symbol_info['symbol'].startswith(symbols_to_fetch) for symbols_to_fetch in symbols_to_fetch))
        )

    @staticmethod
    def update_prices_from_binance(queryset=None):
        queryset = queryset or Symbol.relevant.all()
        symbols = []
        for symbol in queryset:
            symbol.price = binance_client.client().get_avg_price(symbol=symbol.symbol)['price']
            symbols.append(symbol)
        Symbol.objects.bulk_update(symbols, ['price'])

    def __str__(self):
        return '%s' % (self.symbol)

    class Meta:
        ordering = ['symbol']


class SpotOrder(models.Model):
    STATUS = (
        (Client.ORDER_STATUS_NEW, 'New'),
        (Client.ORDER_STATUS_PARTIALLY_FILLED, 'Partially filled'),
        (Client.ORDER_STATUS_FILLED, 'Filled'),
        (Client.ORDER_STATUS_CANCELED, 'Cancelled'),
        (Client.ORDER_STATUS_PENDING_CANCEL, 'Pending cancel'),
        (Client.ORDER_STATUS_REJECTED, 'Rejected'),
        (Client.ORDER_STATUS_EXPIRED, 'Expired'),
    )
    SIDE = (
        (Client.SIDE_BUY, 'Buy'),
        (Client.SIDE_SELL, 'Sell')
    )

    order_id = models.BigIntegerField(unique=True)
    client_order_id = models.CharField(max_length=100, unique=True)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='orders')
    price = models.DecimalField(decimal_places=8, max_digits=18)
    executed_quantity = models.DecimalField(decimal_places=8, max_digits=18)
    cummulative_quote_quantity = models.DecimalField(decimal_places=8, max_digits=18)
    status = models.CharField(choices=STATUS, max_length=50)
    side = models.CharField(choices=SIDE, max_length=5)
    timestamp = models.BigIntegerField()
    created_datetime = models.DateTimeField(auto_now_add=True)

    @property
    def gains_losses(self):
        if self.side == Client.SIDE_BUY:
            prof = self.symbol.price - self.price
        else:
            prof = self.price - self.symbol.price
        return prof * self.executed_quantity

    @staticmethod
    @admin.action(description='Import/Update')
    def import_update_from_binance():
        symbols = Symbol.relevant.all()
        for symbol in symbols:
            orders = binance_client.get_all_orders(symbol=symbol.symbol)
            for order in orders:
                if order['status'] == Client.ORDER_STATUS_FILLED:
                    a, created = SpotOrder.objects.update_or_create(
                        order_id=order['orderId'],
                        client_order_id=order['clientOrderId'],
                        symbol=symbol,
                        defaults={
                            'price': order['price'],
                            'executed_quantity': order['executedQty'],
                            'cummulative_quote_quantity': order['cummulativeQuoteQty'],
                            'status': order['status'],
                            'timestamp': order['time'],
                            'side': order['side']
                        }
                    )

    class Meta:
        ordering = ['symbol']
