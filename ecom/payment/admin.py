from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, PurchaseHistory
from django.contrib.auth.models import User

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PurchaseHistory)
#create an orderitem inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
# extend our order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    #to get things we want and things we don't want in the order admin dashboard
    # fields = ["user", "full_name", "email"]
    inlines = [OrderItemInline]

#unregister order model
admin.site.unregister(Order)

#Re-register our order AND orderadmin
admin.site.register(Order, OrderAdmin)