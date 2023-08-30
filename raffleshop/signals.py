from django.dispatch import receiver
from django.db.models.signals import post_save
from raffleshop.models import UserProfile, ShoppingCart
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        shopping_cart = ShoppingCart.objects.create()
        UserProfile.objects.create(user=instance, shopping_cart=shopping_cart)
