import threading

from django.contrib import admin


# Register your models here.
from django.utils.html import format_html

from core import models


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ['id']


@admin.action(description='Update prices')
def update_symbol_prices(modeladmin, request, queryset):
    def _update_symbol_prices():
        models.Symbol.update_prices_from_binance(queryset)
    threading.Thread(target=_update_symbol_prices())


class SymbolModelAdmin(BaseModelAdmin):
    fields = ['id', 'symbol', 'price', 'updated_datetime']
    list_display = ['symbol', 'price', 'updated_datetime']
    readonly_fields = ['id', 'price', 'updated_datetime']
    actions = [update_symbol_prices]


class SpotOrderModelAdmin(BaseModelAdmin):
    fields = ['id', 'order_id', 'client_order_id', 'symbol', 'price', 'executed_quantity', 'cummulative_quote_quantity', 'status', 'timestamp']
    list_display = ['symbol', 'price', 'executed_quantity', 'gains_losses', 'side']
    readonly_fields = ['id', 'order_id', 'client_order_id', 'symbol', 'price', 'executed_quantity', 'cummulative_quote_quantity', 'status', 'timestamp']
    list_filter = ['side']

    def gains_losses(self, obj):
        color = 'AAB7B8'
        if obj.gains_losses > 0:
            color = '008000'
        elif obj.gains_losses < 0:
            color = 'FF3346'
        return format_html('<span style="color: #{};">{}</span>', color, obj.gains_losses)


admin.site.register(models.Symbol, SymbolModelAdmin)
admin.site.register(models.SpotOrder, SpotOrderModelAdmin)
