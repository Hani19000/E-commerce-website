from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save

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