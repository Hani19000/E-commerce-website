from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Customer, Product, Order, Tag, Trademark, Profile, CustomUser

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Tag)
admin.site.register(Trademark)
admin.site.register(Profile)


#Mix profile info and user info
class ProfileInLine(admin.StackedInline):
    model = Profile

#Extend User Model
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "usable_password", "password1", "password2"),
            },
        ),
    )

#Unregister the old way
# admin.site.unregister(CustomUser)

#Re-register the new way
admin.site.register(CustomUser, CustomUserAdmin)