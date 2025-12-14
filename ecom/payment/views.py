from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
import requests
import certifi
from store.models import Profile
from django.views import View
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from payment.models import PurchaseHistory
from store.models import Product
# from django.urls import reverse
# from paypal.standard.forms import PayPalPaymentsForm
# from django.conf import settings
# import uuid #unique user id for duplicate orders

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
    


def create_stripe_checkout(request):
    """Crée une session Stripe quand l'utilisateur clique sur 'Pay with Stripe'"""
    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée")
        return redirect('billing_info')
    
    # Récupérer le panier
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.cart_total()
    
    if not cart_products or total <= 0:
        messages.error(request, "Votre panier est vide")
        return redirect('cart_summary')
    
    # Récupérer les infos de livraison depuis la session
    my_shipping = request.session.get('my_shipping')
    if not my_shipping:
        messages.error(request, "Veuillez d'abord renseigner vos informations de livraison")
        return redirect('checkout')
    
    # Fonction helper pour nettoyer les données
    def clean_shipping_data(data):
        """Nettoie les données de shipping pour extraire les valeurs"""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, list):
                # Si c'est une liste, prendre le premier élément
                cleaned[key] = value[0] if value else ''
            else:
                cleaned[key] = value
        return cleaned
    
    # Nettoyer les données de shipping
    clean_shipping = clean_shipping_data(my_shipping)
    
    try:
        # Créer les line items pour Stripe
        line_items = []
        for product in cart_products:
            quantity = quantities.get(str(product.id), 1)
            price = product.sale_price if product.is_sale else product.price
            
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(float(price) * 100),
                    'product_data': {
                        'name': product.name,
                        'description': product.description[:100] if hasattr(product, 'description') and product.description else '',
                    },
                },
                'quantity': quantity,
            })
        
        # Créer la session Stripe
        YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
        
        # Extraire l'email proprement
        customer_email = clean_shipping.get('shipping_email', '')
        product_ids = [str(p.id) for p in cart_products]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/payment/payment_success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/payment/billing_info/',
            customer_email=customer_email,  # Utiliser la version nettoyée
            metadata={
                'user_id': request.user.id if request.user.is_authenticated else 'guest',
                'email': customer_email,
                'product_ids': ",".join(product_ids),
                'product_prices': ",".join([str(product.sale_price if product.is_sale else product.price) for product in cart_products]),
            }
        )
        
        # Stocker l'ID de session pour validation ultérieure
        request.session['stripe_session_id'] = checkout_session.id
        request.session['stripe_shipping_info'] = clean_shipping  # Sauvegarder la version nettoyée
        
        # Rediriger vers Stripe
        return redirect(checkout_session.url)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création du paiement Stripe: {str(e)}")
        return redirect('billing_info')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        stripe_session_id = session.get('id')

        # 🔒 Anti-doublon Stripe
        if PurchaseHistory.objects.filter(stripe_session_id=stripe_session_id).exists():
            return HttpResponse(status=200)

        metadata = session.get('metadata', {})
        product_ids = metadata.get('product_ids', '').split(',')
        product_prices = metadata.get('product_prices', '').split(',')
        user_id = metadata.get('user_id')

        if not product_ids or not product_prices or len(product_ids) != len(product_prices):
            return HttpResponse(status=200)

        user = None
        if user_id and user_id != 'guest':
            user = User.objects.filter(id=user_id).first()

        purchased_items = []
        total_amount = 0

        for pid, price_str in zip(product_ids, product_prices):
            try:
                product = Product.objects.get(id=pid)
                price = float(price_str)
                PurchaseHistory.objects.create(
                    user=user,
                    product=product,
                    quantity=1,
                    price=price,
                    purchase_success=True,
                    stripe_session_id=stripe_session_id
                )
                purchased_items.append({
                    'product': product,
                    'quantity': 1,
                    'price': price,
                    'total': price * 1
                })
                total_amount += price
            except Product.DoesNotExist:
                continue

        # ----- ENVOI EMAIL ----- #
        if user and user.email:
            mail_subject = "Paiement accepté ✅"
            message = render_to_string("payment/payment_success_email.html", {
                'user': user,
                'items': purchased_items,
                'order': {
                    'id': stripe_session_id,
                    'amount_paid': total_amount,
                    'date_ordered': session.get('created'),  # timestamp Stripe
                    'date_shipped': session.get('created'),  # exemple
                    'full_name': user.get_full_name(),
                    'shipping_address': metadata.get('shipping_address', '')
                },
                'domain': get_current_site(request).domain,
                'protocol': 'https' if request.is_secure() else 'http',
            })
            try:
                url = "https://api.sendgrid.com/v3/mail/send"
                headers = {
                    "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "personalizations": [{
                        "to": [{"email": user.email}],
                        "subject": mail_subject
                    }],
                    "from": {"email": settings.SENDGRID_FROM_EMAIL, "name": "Votre Boutique"},
                    "content": [{"type": "text/html", "value": message}]
                }
                response = requests.post(url, headers=headers, json=data, verify=certifi.where(), timeout=10)
                if response.status_code != 202:
                    print(f"SendGrid error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Erreur en envoyant l'email de paiement: {e}")

    return HttpResponse(status=200)







def billing_info(request):
    """Affiche la page de billing avec le résumé de commande"""
    # Récupérer le panier
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    
    # Vérifier si le panier est vide
    if not cart_products or totals <= 0:
        messages.error(request, "Votre panier est vide")
        return redirect('cart_summary')
    
    if request.method == 'POST':
        # Créer une session avec les infos de livraison
        my_shipping = request.POST
        request.session['my_shipping'] = dict(request.POST)
        
        # Vérifier si l'utilisateur est connecté
        if request.user.is_authenticated:
            # Utilisateur connecté
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form
            })
        else:
            # Guest checkout
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': request.POST, 'billing_form': billing_form})
    
    else:  # GET request (retour de Stripe ou accès direct)
        # Récupérer les infos de shipping depuis la session
        my_shipping = request.session.get('my_shipping')
        
        if not my_shipping:
            messages.warning(request, "Veuillez d'abord remplir vos informations de livraison")
            return redirect('checkout')
        
        # Afficher la page pour les deux types d'utilisateurs
        if request.user.is_authenticated:
            # Utilisateur connecté
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': my_shipping, 'billing_form': billing_form})
        else:
            # Guest checkout
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': my_shipping,'billing_form': billing_form})
    


def checkout(request):
    #get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    if request.user.is_authenticated:
        #checkout as loged in user
        #shipping user
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        #shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products": cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})


def payment_success(request):
    return render(request, 'payment/payment_success.html',{})

def payment_failed(request):
    return render(request, 'payment/payment_failed.html',{})