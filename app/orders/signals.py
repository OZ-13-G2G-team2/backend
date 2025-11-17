from django.db.models.signals import post_save
from django.dispatch import receiver

from app.orders.models import OrderItem


@receiver(post_save, sender=OrderItem)
def calculate_total_price_signal(sender, instance, created, **kwargs):
    instance.calculate_total_price()
    instance.save(update_fields=['price_at_purchase'])