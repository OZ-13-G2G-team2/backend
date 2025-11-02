from decimal import Decimal
from .constants import STATUS_CHOICES


def calculate_order_total(order_items):
    total = sum([item.quantity * item.price_at_purchase for item in order_items])
    return Decimal(total).quantize(Decimal("0.01"))


def format_order_status(status):
    status_dict = dict(STATUS_CHOICES)
    return status_dict.get(status, status)
