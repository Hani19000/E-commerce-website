from django.shortcuts import render, redirect
from .models import Product, Category, Tag, Trademark, Profile
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm 
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, SignInForm, PasswordResetForm, SetPasswordForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.db.models.query_utils import Q
import json
from cart.cart import Cart
from django.conf import settings
import requests
import certifi

# User = get_user_model()

def search(request):
    #determin if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        #query the prodct DB model
        searched = Product.objects.filter(name__icontains=searched)
        #test for null
        if not searched :
            messages.error(request, "you must be loged in to acces to that page")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {'searched':searched})
    else:
        return render(request, "search.html", {})

def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user, created = Profile.objects.get_or_create(user=request.user)
        #get current users shipping info

        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        #get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #get users's shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            #save original form
            form.save()
            #save shipping form
            shipping_form.save()
            messages.success(request, "Your info has been updated")
            return redirect ('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form':shipping_form})
    else:
        messages.error(request, "you must be loged in to acces to that page")
        return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "your password has been updated...")
                login(request, current_user)
                return redirect('home')
            else :
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.error(request, "you must be loged in to acces to that page")
        return redirect('home')
    

#####  avec sendgrid  #######
def send_password_reset_email(request, user, to_email):
    """
    Envoie un email de réinitialisation de mot de passe via SendGrid
    """
    mail_subject = 'Password Reset Request - Your Store'
    
    # Génération du message HTML
    message = render_to_string('reset_password.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": mail_subject
            }],
            "from": {
                "email": settings.SENDGRID_FROM_EMAIL,
                "name": "Your Store Security"
            },
            "reply_to": {
                "email": settings.SENDGRID_FROM_EMAIL,
                "name": "Your Store Support"
            },
            "content": [{
                "type": "text/html",
                "value": message
            }],
            "tracking_settings": {
                "click_tracking": {"enable": True},
                "open_tracking": {"enable": True}
            },
            "mail_settings": {
                "bypass_list_management": {"enable": False},
                "footer": {"enable": False},
                "sandbox_mode": {"enable": False}
            },
            "categories": ["password_reset"]
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            verify=certifi.where(), 
            timeout=10
        )
        
        if response.status_code == 202:
            return True
        else:
            print(f"SendGrid error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Email timeout error")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def password_reset_request(request):
    """
    Vue pour gérer la demande de réinitialisation de mot de passe
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            
            if associated_user:
                # Envoyer l'email via SendGrid
                email_sent = send_password_reset_email(request, associated_user, user_email)
                
                if email_sent:
                    messages.success(
                        request, 
                        f"✅ Password reset instructions have been sent to {user_email}. "
                        "Please check your inbox (and spam folder if needed)."
                    )
                else:
                    messages.error(
                        request, 
                        "⚠️ Problem sending reset password email. Please try again later or contact support."
                    )
            else:
                # Pour des raisons de sécurité, on affiche le même message même si l'email n'existe pas
                # Cela évite qu'un attaquant puisse vérifier quels emails sont enregistrés
                messages.success(
                    request,
                    f"If an account exists with {user_email}, you will receive password reset instructions."
                )
            
            return redirect('home')
        
        # Gestion des erreurs du formulaire
        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, '⚠️ You must pass the reCAPTCHA test!')
                continue
            messages.error(request, error)
    
    else:
        form = PasswordResetForm()
    
    return render(
        request=request, 
        template_name="password_reset.html", 
        context={"form": form}
    )



# def password_reset_request(request):
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             user_email = form.cleaned_data['email']
#             associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
#             if associated_user:
#                 subject = "Password Reset Request"
#                 message = render_to_string("reset_password.html",{
#                     'user' : associated_user,
#                     'domain': get_current_site(request).domain,
#                     'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
#                     'token': account_activation_token.make_token(associated_user),
#                     "Protocol" : 'https' if request.is_secure() else 'http'
#                 })
#             email = EmailMessage(subject, message, to=[associated_user.email])
#             if email.send():
#                     messages.success(request,"your reset password has been sent, do the instruction send in your email")
#             else:
#                     messages.error(request, "probleme sending reset password email, <b>SERVER PROBLEM</b>")
#             return redirect('home')
    
#         for key, error in list(form.errors.items()):
#                 if key == 'captcha' and error[0] == 'This field is required.':
#                     messages.error(request, 'you must pass the recaptcha test !')
#                     continue


#     form = PasswordResetForm()
#     return render(request=request, template_name="password_reset.html", context={"form": form})



def PasswordResetConfirm (request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user= User.objects.get(pk=uid)
    except:
        user=None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password has been set. You may go ahead and login now")
                return redirect(('login'))
            else : 
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render (request=request, template_name='password_reset_confirm.html', context={'form': form})
    else:
        messages.error(request, "alink is expired")
    messages.error(request, 'something went wrong, redirecting back to homepage')
    return redirect(('home'))

def update_user(request):
    if request.user.is_authenticated:
        current_user = request.user
        user_form = UpdateUserForm (request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "user has been Updated")
            return redirect ('home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.error(request, "you must be loged in to acces to that page")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    trademarks = Trademark.objects.all()
    return render(request, "category_summary.html", {'categories': categories, 'products': products, 'trademarks': trademarks})

def category(request, foo):
    #replace hypens with spaces
    foo = foo.replace('-', ' ')
    #grab the category from the url
    try:
        #look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category':category})
    except:
        messages.error(request, ("that category dosen't exist !"))
        return redirect('home')

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})

def about(request):
    return render(request, 'about.html', {})

def shop (request):
    products = Product.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()
    trademarks = Trademark.objects.all()
    return render(request, 'shop.html', {'products': products, 'categories': categories, 'tags': tags, 'trademarks': trademarks })


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            first_login = user.last_login is None
            login(request, user)
            if user is not None:
                #avoir la session de carte meme quand je me déconnecte
                current_user = Profile.objects.get(user__id=request.user.id)
                #get their saved cart from DB
                saved_cart = current_user.old_cart
                #convert db str to python dictionary {"3",2, "4":5} to dictionary
                if saved_cart :
                    #convert dictionary using JSON
                    converted_cart = json.loads(saved_cart)
                    # add the loaded cart dictionary to our session
                    # get the cart
                    cart= Cart(request)
                    #loop thru the cart and add thetems from the db
                    for key, value in converted_cart.items():
                        cart.db_add(product=key, quantity=value)
                messages.success(request, ('Welcom you have been logged in !'))
                if first_login:
                    return redirect('update_info')
                else:
                    return redirect('home')
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, 'you must pass the recaptcha test !')
                    continue
                messages.error(request, error)
    else:
        form = SignInForm()
    
    return render(request, template_name='login.html', context={'form': form})



def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out !'))
    return redirect('home')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user= User.objects.get(pk=uid)
    except:
        user=None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "thank you for you'r email confirmation. Now you can login your account")
        return redirect ('login')
    else:
        messages.error(request, "activation link is invalid")

    return redirect ('home')

import requests
from django.conf import settings

def activateEmail(request, user, to_email):
    import certifi
    
    # Titre professionnel et clair
    mail_subject = 'Activate Your Account - Action Required'
    
    # Génération du message HTML
    message = render_to_string('activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": mail_subject
            }],
            "from": {
                "email": settings.SENDGRID_FROM_EMAIL,
                "name": "Your Store Team"  # Nom professionnel
            },
            "reply_to": {
                "email": settings.SENDGRID_FROM_EMAIL,
                "name": "Your Store Support"
            },
            "content": [{
                "type": "text/html",
                "value": message
            }],
            # IMPORTANT: Paramètres anti-spam
            "tracking_settings": {
                "click_tracking": {"enable": True},
                "open_tracking": {"enable": True}
            },
            "mail_settings": {
                "bypass_list_management": {"enable": False},
                "footer": {"enable": False},
                "sandbox_mode": {"enable": False}
            },
            # Catégorie pour le tracking
            "categories": ["account_activation"]
        }
        
        response = requests.post(url, headers=headers, json=data, verify=certifi.where(), timeout=10)
        
        if response.status_code == 202:
            messages.success(request, f'✅ Activation email sent to {to_email}. Please check your inbox (and spam folder if needed).')
        else:
            print(f"SendGrid error: {response.status_code} - {response.text}")
            messages.warning(request, 'Account created but email may be delayed. Please check your spam folder.')
            
    except requests.exceptions.Timeout:
        print("Email timeout error")
        messages.warning(request, "Email sending timed out. Please check your spam folder.")
    except Exception as e:
        print(f"Error sending email: {e}")
        messages.warning(request, "Account created. If you don't receive an email, please check your spam folder.")

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Envoi email
            activateEmail(request, user, form.cleaned_data.get('email'))
            
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'register.html', {'form': form})





## utiliser resend 
#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
# resend.api_key = settings.RESEND_API_KEY

# def send_email_with_resend(subject, message, to_email):
#     try:
#         resend.Emails.send({
#             "from": "hanider27@gmail.com",  # or your verified domain
#             "to": to_email,
#             "subject": subject,
#             "html": message
#         })
#     except Exception as e:
#         print(f"Error sending email: {e}")


# def activateEmail(request, user, to_email):
#     mail_subject = 'Activate your user account.'
#     message = render_to_string('activate_account.html', {
#         'user': user.username,
#         'domain': get_current_site(request).domain,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': account_activation_token.make_token(user),
#         'protocol': 'https' if request.is_secure() else 'http'
#     })
    
#     try:
#         resend.Emails.send({
#             "from": "onboarding@resend.dev",
#             "to": "hanider27@gmail.com",  # Email de test Resend
#             "subject": mail_subject,
#             "html": message
#         })
#         messages.success(request, f'Activation email sent! (Test mode: check Resend dashboard)')
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         messages.error(request, "Error sending activation email.")

# def register_user(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
            
#             # Envoi email (non bloquant maintenant)
#             activateEmail(request, user, form.cleaned_data.get('email'))
            
#             # Redirection immédiate
#             return redirect('home')
#     else:
#         form = SignUpForm()
    
#     return render(request, 'register.html', {'form': form})















# def activateEmail(request, user, to_email):
#     mail_subject = "Activate your user account"
#     message = render_to_string("activate_account.html",{
#         'user' : user,
#         'domain': get_current_site(request).domain,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': account_activation_token.make_token(user),
#         "Protocol" : 'https' if request.is_secure() else 'http'

#     })
#     email = EmailMessage(mail_subject, message, to=[to_email])
#     if email.send():
#         messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on received activation link to confirm and complete the registration. <b>Note:</b> check your spam folder.')
#     else :
#         messages.error(request, f'Probleme sending email to {to_email}, check if you typed it correctly.')


# def register_user(request):
#     form = SignUpForm()
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             # username = form.cleaned_data['username']
#             # password = form.cleaned_data['password1']
#             user.is_active=False
#             user.save()
#             activateEmail(request,user, form.cleaned_data.get('email'))
#             # messages.success(request, ('Username Created - Please fill out your info below..(not requied)!'))
#             return redirect('home')

#             #log in user
#             # login(request, user)
#             # messages.success(request, ('Username Created - Please fill out your info below..(not requied)!'))
#             # return redirect('update_info')
#         else:
#             # messages.error(request, ('there was an error!'))
#             # return render(request, 'register.html', {'form': form})
#             for error in list(form.errors.values()):
#                 messages.error(request, error)
#     else:
#         form = SignUpForm()

#     return render (request=request, template_name= 'register.html', context={'form':form})