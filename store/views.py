from django.shortcuts import render, redirect
from .models import Product, Category, Tag, Trademark, Profile
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm 
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, SignInForm
from django import forms
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
User = get_user_model()



def update_info(request):
    if request.user.is_authenticated:
        current_user, created = Profile.objects.get_or_create(user=request.user)
        form = UserInfoForm(request.POST or None, instance=current_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your info has been updated")
            return redirect ('home')
        return render(request, "update_info.html", {'form': form})
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
            
            if user is not None:
                first_login = user.last_login is None
                login(request, user)
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
    
    return render(request, 'login.html', {'form': form})


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

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account"
    message = render_to_string("activate_account.html",{
        'user' : user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "Protocol" : 'https' if request.is_secure() else 'http'

    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on received activation link to confirm and complete the registration. <b>Note:</b> check your spam folder.')
    else :
        messages.error(request, f'Probleme sending email to {to_email}, check if you typed it correctly.')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # username = form.cleaned_data['username']
            # password = form.cleaned_data['password1']
            user.is_active=False
            user.save()
            activateEmail(request,user, form.cleaned_data.get('email'))
            # messages.success(request, ('Username Created - Please fill out your info below..(not requied)!'))
            return redirect('home')

            #log in user
            # login(request, user)
            # messages.success(request, ('Username Created - Please fill out your info below..(not requied)!'))
            # return redirect('update_info')
        else:
            # messages.error(request, ('there was an error!'))
            # return render(request, 'register.html', {'form': form})
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = SignUpForm()

    return render (request=request, template_name= 'register.html', context={'form':form})