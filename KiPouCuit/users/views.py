from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

#------------sign up------------
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/signup.html')

        # create user
        user = User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'users/signup.html')

#------------log in------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace with your homepage URL
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'users/login.html')

    return render(request, 'users/login.html')

#------------forgot password------------
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        messages.success(request, f"Password reset link sent to {email}!")
        return render(request, 'users/forgot_password.html')

    return render(request, 'users/forgot_password.html')

def create_account(request):
    days = range(1, 32)   # 1–31
    months = range(1, 13) # 1–12
    years = range(1900, 2026)  # adjust as needed
    return render(request, "users/create_account.html", {
        "days": days,
        "months": months,
        "years": years,
    })

def user_history_view(request):
    return render(request, 'users/user_history.html')



