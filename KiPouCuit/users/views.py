from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth import login

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1️⃣ Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            # 2️⃣ Return the same form with filled-in values
            return render(request, 'users/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address
            })

        # 3️⃣ Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'users/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address
            })

        # 4️⃣ Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # 5️⃣ Create profile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address
        )

        # 6️⃣ Log in user automatically
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect('home')

    # 7️⃣ Normal page load (GET request)
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

def user_profile_view(request):
    return render(request, 'users/user_profile.html')




