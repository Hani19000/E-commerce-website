from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress
from django.contrib import messages


def payment_success(request):
    return render(request, 'payment/payment_success.html',{})

def checkout(request):
    #get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    if request.user.is_authenticated:
        #checkout as loged in user
        #shipping user
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user.id)
        #shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})


def billing_info(request):
    if request.POST:
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        #check to see if user is logged in
        if request.user.is_authenticated:
            #get the billing form
            billing_form = PaymentForm
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form})
        else:
            billing_form = PaymentForm
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form})

        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})

    else:
        messages.error(request, "Acces denied")
        return redirect ('home')