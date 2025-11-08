from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review

# Create your views here.

def review(request):
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
            return redirect('review')
        else:
            messages.error(request, '⚠️ Please fill in all fields before submitting.')

    return render(request, 'reviews/review.html')

def review_list(request):
    reviews = Review.objects.all().order_by('-id')  # newest first
    return render(request, 'reviews/review_list.html', {'reviews': reviews})