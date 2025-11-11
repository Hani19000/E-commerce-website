from django.shortcuts import render, redirect
from .models import Product, Category, Tag, Trademark
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm
from django import forms


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #did they fill out the form
        if request.method == 'POST':
            pass
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.success(request, "you must be loged in to acces to that page")
        return redirect('home')
    

def update_user(request):
    if request.user.is_authenticated:
        current_user =   User.objects.get(id=request.user.id)
        user_form = UpdateUserForm (request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "user has been Updated")
            return redirect ('home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "you must be loged in to acces to that page")
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, ('Welcom you have been logged in !'))
            return redirect('home')
        else:
            messages.error(request, ('there was an error, try again !'))
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out !'))
    return redirect('home')



def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('You have registered succefly !'))
            return redirect('home')
        else:
            messages.error(request, ('there was an error!'))
            return render(request, 'register.html', {'form': form})
    else:
        return render (request, 'register.html', {'form':form})