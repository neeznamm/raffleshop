from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


class Series(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products_in_series', default=None)

    def __str__(self):
        return str(self.name)


class SeriesImage(models.Model):
    description = models.CharField(
        max_length=250, default="No description for image.")
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to='series_images', blank=True)

    def __str__(self):
        return str(self.description)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="products", blank=True, null=True)

    def __str__(self):
        return str(self.name)


class ProductImage(models.Model):
    description = models.CharField(
        max_length=250, default="No description for image.")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to='product_images', blank=True)

    def __str__(self):
        return str(self.description)


class ShippingInfo(models.Model):

    LOCATION_CHOICES = (('US', 'United States'),
                        ('EU', 'Europe'),
                        ('CA', 'Central Asia'),
                        ('EA', 'Eastern Asia'),
                        ('SOA', 'Southern Asia'),
                        ('SEA', 'South-Eastern Asia'),
                        ('WA', 'Western Asia'),
                        ('MENA', 'Middle East & North Africa'),
                        ('SA', 'South America'),
                        ('RU', 'Russia'))

    shipping_locations = MultiSelectField(
        choices=LOCATION_CHOICES, max_length=26)
    width = models.DecimalField(max_digits=11, decimal_places=2)
    height = models.DecimalField(max_digits=11, decimal_places=2)
    depth = models.DecimalField(max_digits=11, decimal_places=2)
    weight = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return str(f'width:{self.width} x height:{self.height} x weight:{self.weight} x depth:{self.depth} : {self.shipping_locations}')


class ShoppingCart(models.Model):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile")
    shopping_cart = models.OneToOneField(
        ShoppingCart, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username)


class DeliveryAddress(models.Model):
    city = models.CharField(max_length=128)
    street = models.TextField()
    postal_code = models.CharField(max_length=10)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_addresses")


class PaymentInfo(models.Model):
    class CardType(models.TextChoices):
        VISA = 'VIS', 'Visa'
        MASTERCARD = 'MAS', 'MasterCard'
        PAYONEER = 'PAY', 'Payoneer'
        MAESTRO = 'MAE', 'Maestro'

    card_type = models.CharField(
        max_length=3, choices=CardType.choices, default=CardType.VISA)
    card_number = models.CharField(max_length=255)
    name_on_card = models.CharField(max_length=255)
    cvv = models.CharField(max_length=3)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_infos")

    def __str__(self):
        return str(f'{self.card_type} {self.name_on_card}')


class Raffle(models.Model):
    begin_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="raffles")
    product_price = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    ticket_price = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    num_pairs = models.IntegerField()
    shipping_info = models.ForeignKey(
        ShippingInfo, on_delete=models.CASCADE, related_name="raffles", null=True, blank=True)

    def __str__(self):
        return str(f'{self.product} : pprice:{self.product_price} : tprice:{self.ticket_price} : numpairs:{self.num_pairs}')


class Ticket(models.Model):
    checked_out = models.BooleanField(default=False)
    raffle = models.ForeignKey(
        Raffle, on_delete=models.CASCADE, related_name="tickets")
    shopping_cart = models.ForeignKey(
        ShoppingCart, on_delete=models.CASCADE, related_name="tickets")
