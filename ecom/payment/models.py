from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from store.models import Product
from django.dispatch import receiver
import datetime

class ShippingAddress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.EmailField( max_length=255)
    shipping_address1 =models.CharField(max_length=200)
    shipping_address2=models.CharField(max_length=200)
    shipping_city= models.CharField(max_length=200)
    shipping_state= models.CharField(max_length=200)
    shipping_zipcode= models.CharField(max_length=200)
    shipping_country= models.CharField(max_length=200)


    class Meta :
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'shipping address-{str(self.id)}'
    
def create_ShippingAddress(sender, instance, created, **kwargs):
    if created :
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

#automate the profile
post_save.connect(create_ShippingAddress, sender=User)

#order model
class Order(models.Model):
    #foreign key
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField( max_length=255)
    shipping_address =models.CharField(max_length=20000)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=7)
    date_ordered = models.DateField(auto_now_add=True)
    shipped = models.BooleanField(default = False)
    date_shipped = models.DateTimeField(blank=True, null=True, )

    def __str__(self):
        return f'Order-{str(self.id)}'

# Add auto shipping date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now


#order items model
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Order Item-{str(self.id)}'