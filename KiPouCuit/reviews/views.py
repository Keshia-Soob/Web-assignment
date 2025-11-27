from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem


@login_required(login_url='login')
def review(request):
    user = request.user  # the logged-in user

    user_orders = Order.objects.filter(user=user)
    completed_orders = 0

    for order in user_orders:
        statuses = set(order.items.values_list('status', flat=True))
        if statuses == {OrderItem.Status.DELIVERED}:  
            completed_orders += 1

    if completed_orders < 1:
        messages.error(request, "You must complete at least ONE delivered order before posting a review.")
        return render(request, 'reviews/review.html', {
            'blocked': True
        })

    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }

    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        rating = request.POST.get('rating')
        message = request.POST.get('message')

        if first_name and last_name and email and rating and message:
            Review.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                rating=rating,
                message=message
            )
            messages.success(request, '✅ Your review has been posted successfully!')
            return redirect('review_list')
        else:
            messages.error(request, '⚠️ Please fill in all fields before submitting.')

    return render(request, 'reviews/review.html', {'initial_data': initial_data})

def review_list(request):
    reviews = Review.objects.all().order_by('-id') 
    return render(request, 'reviews/review_list.html', {'reviews': reviews})