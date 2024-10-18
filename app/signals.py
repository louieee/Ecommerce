from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import ProductSale


@receiver(post_save, sender=ProductSale)
def update_product_stock(instance, created, **kwargs):
    if created:
        batch = instance.product_unit.current_batch
        quantity = instance.quantity
        batch.quantity = F("quantity") - quantity
        batch.save()