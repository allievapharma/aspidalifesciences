from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Category, SubCategory, Product
from .utils import generate_unique_slug


@receiver(pre_save, sender=Category)
def category_slug_handler(sender, instance, **kwargs):
    if not instance.slug or instance.name:
        instance.slug = generate_unique_slug(instance, instance.name)


@receiver(pre_save, sender=SubCategory)
def subcategory_slug_handler(sender, instance, **kwargs):
    if not instance.slug or instance.name:
        instance.slug = generate_unique_slug(instance, instance.name)


@receiver(pre_save, sender=Product)
def product_slug_handler(sender, instance, **kwargs):
    if not instance.slug or instance.name:
        instance.slug = generate_unique_slug(instance, instance.name)
