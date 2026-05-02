from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfilePhotoForm
from orders.models import Order, OrderItem


def get_user_orders(user):
    
    return Order.objects.filter(user=user).prefetch_related('items__menu_item').order_by('-created_at')


def signup_view(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

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

      
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )


        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone or profile.phone
        profile.address = address or profile.address
        profile.save()

        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect('home')

    return render(request, 'users/signup.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'users/login.html')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            messages.success(request, f"A password reset link has been sent to {email}. Please check your inbox.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")

        return render(request, 'users/forgot_password.html')

    return render(request, 'users/forgot_password.html')


@login_required
def user_history_view(request):

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders_qs = get_user_orders(request.user)

    orders_meta = []
    for order in orders_qs:
        
        try:
            overall_status = getattr(order, "status", None)
            if overall_status is None:
                statuses = set(order.items.values_list("status", flat=True))
                if not statuses:
                    overall_status = "pending"
                elif statuses == {OrderItem.Status.DELIVERED}:
                    overall_status = "delivered"
                elif OrderItem.Status.DELIVERING in statuses:
                    overall_status = "delivering"
                elif OrderItem.Status.ACCEPTED in statuses:
                    overall_status = "accepted"
                else:
                    overall_status = "pending"
        except Exception:
            overall_status = "pending"

        mapping = {
            "pending": "Pending (kitchen)",
            "accepted": "Accepted by cook",
            "delivering": "Is being delivered",
            "delivered": "Delivered",
        }
        overall_text = mapping.get(overall_status, overall_status)

        has_accepted = order.items.filter(status=OrderItem.Status.ACCEPTED).exists()
        has_delivering = order.items.filter(status=OrderItem.Status.DELIVERING).exists()

        orders_meta.append({
            "order": order,
            "overall_status": overall_status,
            "overall_text": overall_text,
            "has_accepted": has_accepted,
            "has_delivering": has_delivering,
        })

    return render(request, "users/user_history.html", {
        "profile": profile,
        "orders_meta": orders_meta,
    })


@login_required
def user_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfilePhotoForm(instance=profile)

    return render(request, 'users/user_profile.html', {'profile': profile, 'form': form})
