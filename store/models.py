from django.db import models
import datetime

#Category of products
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
    class Meta:
        verbose_name_plural = 'Categories'


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
    class Meta:
        verbose_name_plural = 'tags'


class Trademark(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
    class Meta:
        verbose_name_plural = 'trademarks'

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)
    trademark = models.ForeignKey(Trademark, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/products/', blank=True, null=True)
    # add sale
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name

#Customer Orders
class Order(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=10, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product
    