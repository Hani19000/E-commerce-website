from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
import datetime
from store.models import Profile

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-id')
        
        # Calculer les statistiques
        shipped_count = orders.filter(shipped=True).count()
        pending_count = orders.filter(shipped=False).count()
        
        context = {
            'orders': orders,
            'shipped_count': shipped_count,
            'pending_count': pending_count,
        }
        
        return render(request, 'payment/my_orders.html', context)
    else:
        messages.error(request, "Vous devez être connecté pour voir vos commandes")
        return redirect('login')

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status']
            
            # Check if true or false
            if status == "true":
                # Get the order
                order_obj = Order.objects.filter(id=pk)
                # Update the status
                now = datetime.datetime.now()
                order_obj.update(shipped=True, date_shipped=now)
                
                # Send email notification
                order = order_obj.first()  # Get the updated order object
                if order and order.user:  # Verify order and user exist
                    subject = "Votre commande a été expédiée ! 📦"
                    
                    # Render email template
                    message = render_to_string("payment/order_shipped_email.html", {
                        'user': order.user,
                        'order': order,
                        'items': items,
                        'domain': get_current_site(request).domain,
                        'protocol': 'https' if request.is_secure() else 'http',
                        'date_shipped': now.strftime('%d/%m/%Y à %H:%M'),
                    })
                    
                    # Send email
                    email = EmailMessage(
                        subject=subject,
                        body=message,
                        to=[order.user.email]
                    )
                    email.content_subtype = "html"  # Important for HTML emails
                    
                    if email.send():
                        messages.success(request, f"Commande marquée comme expédiée et email envoyé à {order.user.email}")
                    else:
                        messages.error(request, "Commande expédiée mais erreur lors de l'envoi de l'email")
                else:
                    messages.error(request, "Commande expédiée mais utilisateur introuvable pour l'envoi d'email")
                    
            else:
                # Get the order
                order_obj = Order.objects.filter(id=pk)
                # Update the status
                order_obj.update(shipped=False, date_shipped=None)
                messages.success(request, "Statut d'expédition mis à jour (non expédié)")
                
            return redirect("home")
        
        return render(request, 'payment/orders.html', {"order": order, "items": items})
    else:
        messages.error(request, "Accès refusé, seuls les administrateurs peuvent accéder à cette page")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            num = request.POST['num']
            now = datetime.datetime.now()
            
            try:
                order = Order.objects.get(id=num)
            except Order.DoesNotExist:
                messages.error(request, "Commande introuvable")
                return redirect("home")
            
            # Mettre à jour la commande
            order.shipped = True
            order.date_shipped = now
            order.save()
            
            # Envoyer l'email au client
            if order.user and order.user.email:
                # Récupérer tous les articles de la commande
                items = OrderItem.objects.filter(order=order)
                
                subject = "Votre commande a été expédiée !"
                message = render_to_string("payment/order_shipped_email.html", {
                    'user': order.user,
                    'order': order,
                    'items': items,  # Passer les articles
                    'domain': get_current_site(request).domain,
                    'protocol': 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[order.user.email])
                email.content_subtype = "html"  # Important pour afficher le HTML
                
                if email.send():
                    messages.success(request, "Statut d'expédition mis à jour et email envoyé au client")
                else:
                    messages.warning(request, "Statut mis à jour mais erreur lors de l'envoi de l'email")
            else:
                messages.success(request, "Statut d'expédition mis à jour")
            
            return redirect("home")
        
        return render(request, "payment/not_shipped_dash.html", {'orders': orders})
    else:
        messages.error(request, "Accès refusé, seuls les administrateurs ont accès à cette page")
        return redirect('home')
    

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            # status = request.POST['shipping_status']
            num = request.POST['num']
            #get the order (evite l'errur order is not defined)
            order = Order.objects.filter(id=num)
            #grab date and time
            now = datetime.datetime.now()
            #update order
            order.update(shipped=False, date_shipped = now)

            
            messages.success(request, "shipping status updated")
            return redirect("shipped_dash")
        return render(request, "payment/shipped_dash.html", {'orders':orders})
    else:
        messages.error(request, "Access denied, only admin user have access this page")
        return redirect ('home')


def process_order(request):
    if request.POST:
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # get billling info from the last page
        payment_form = PaymentForm(request.POST or None)
        #get shipping session data
        my_shipping = request.session.get('my_shipping')

        #gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']


        #create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        #create an order
        if request.user.is_authenticated:
            #logged in
            user = request.user
            #create Order
            create_order = Order(user=user, full_name=full_name, email = email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add order items
            # get the order ID
            order_id = create_order.pk
            #get the product info
            for product in cart_products():
                #get product ID
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else :
                    price = product.price
                # get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItem(order_id=order_id , product_id= product_id, user= user, quantity= value, price=price)
                        create_order_item.save()

            #delete cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete the key
                    del request.session[key]


            #delete cart from db (old_cart field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            # delete shopping cart in db (old_cart field)
            current_user.update(old_cart="")

            messages.success(request, "Order Placed")
            return redirect ('home')
        else :
            #not logged in
            #create order
            create_order = Order(full_name=full_name, email = email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add order items
            # get the order ID
            order_id = create_order.pk
            #get the product info
            for product in cart_products():
                #get product ID
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else :
                    price = product.price
                # get quantity
                for key,value in quantities().items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItem(order_id=order_id , product_id= product_id, quantity= value, price=price)
                        create_order_item.save()

            #delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete the key
                    del request.session[key]

            messages.success(request, "Order Placed")
            return redirect ('home')
        
    else:
        messages.error(request, "Acces denied")
        return redirect ('home')
    

def billing_info(request):
    if request.POST:
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        # create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        #check to see if user is logged in
        if request.user.is_authenticated:
            #get the billing form
            billing_form = PaymentForm
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form})
        else:
            billing_form = PaymentForm
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form})

        # shipping_form = request.POST
        # return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})

    else:
        messages.error(request, "Acces denied")
        return redirect ('home')
    


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


def payment_success(request):
    return render(request, 'payment/payment_success.html',{})