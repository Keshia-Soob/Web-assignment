from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfilePhotoForm

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Prepare context to keep user input in case of error
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address
        }

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/signup.html', context)

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'users/signup.html', context)

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address
        )   

        login(request, user)  # Log the new user in automatically
        messages.success(request, "Welcome! Your account has been created.")
        return redirect('home')

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

#------------log out------------
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page
    
#------------forgot password------------
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            # For assignment purposes, we just simulate sending an email.
            messages.success(request, f"A password reset link has been sent to {email}. Please check your inbox.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")

        return render(request, 'users/forgot_password.html')

    return render(request, 'users/forgot_password.html')

#------------user history------------
def user_history_view(request):
    return render(request, 'users/user_history.html')

#------------user profile------------
@login_required
def user_profile_view(request):
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # reload page to show "Edit Photo"
    else:
        form = UserProfilePhotoForm(instance=profile)

    return render(request, 'users/user_profile.html', {'profile': profile, 'form': form})