from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from .forms import SignUpForm
from django import forms



def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})

def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

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
            user.save()
            login(request, user)
            messages.success(request, ('You have registered succefly !'))
            return redirect('home')
        else:
            messages.error(request, ('there was an error!'))
            return redirect('register')
    else:
        return render (request, 'register.html', {'form':form})