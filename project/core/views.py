import threading

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from core.models import SpotOrder


def import_update_all_orders(request, *args, **kwargs):
    thread = threading.Thread(target=SpotOrder.import_update_from_binance)
    thread.start()
    messages.add_message(request, messages.INFO, 'Import has been started.')
    return redirect(reverse('admin:core_spotorder_changelist'))
