from binance import Client
from django.db import models

# Create your models here.
from django.db.models import Q


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

    class Meta:
        ordering = ['symbol']
