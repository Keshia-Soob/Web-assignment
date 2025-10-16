from django.shortcuts import render, redirect
from django.contrib import messages
from .models import HomeCook

# Create your views here.
def homecook(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        cuisine = request.POST.get('cuisine')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profilePic')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('homecook')

        if HomeCook.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('homecook')

        # Save the new HomeCook record
        HomeCook.objects.create(
            name=name,
            surname=surname,
            email=email,
            password=password,  # (you can later hash this if needed)
            phone=phone,
            address=address,
            cuisine=cuisine,
            bio=bio,
            profile_picture=profile_picture
        )

        messages.success(request, "Your Home Cook account has been created successfully!")
        return redirect('homecook')

    return render(request, 'homecook/homecook.html')

def homecook_log(request):
    # Dummy data for now
    homecook = {
        'name': 'Rajesh Kumar',
        'specialty': 'Indian Cuisine',
        'profile_pic': 'homecook/images/profile.png'
    }

    orders = [
        {
            'dish_name': 'Butter Chicken',
            'qty': 2,
            'client_name': 'Emma Brown',
            'dish_image': 'homecook/images/meal1.png'
        },
        {
            'dish_name': 'Paneer Tikka',
            'qty': 1,
            'client_name': 'Michael Lee',
            'dish_image': 'homecook/images/meal2.png'
        }
    ]

    context = {
        'homecook': homecook,
        'orders': orders
    }

    return render(request, 'homecook/homecook_log.html', context)
