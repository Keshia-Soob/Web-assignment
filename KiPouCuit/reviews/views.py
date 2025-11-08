from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def review(request):
    user = request.user  # the logged-in user

    #Safely get phone from UserProfile
    # contact_number = ''
    # if hasattr(user, 'userprofile'):
    #     contact_number = user.userprofile.phone or ''

    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        # 'phone': contact_number
    }

    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        # phone = request.POST.get('phone') 
        rating = request.POST.get('rating')
        message = request.POST.get('message')

        if first_name and last_name and email and rating and message:
            Review.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                # phone=phone,
                rating=rating,
                message=message
            )
            messages.success(request, '✅ Your review has been posted successfully!')
            return redirect('review_list')
        else:
            messages.error(request, '⚠️ Please fill in all fields before submitting.')

    return render(request, 'reviews/review.html', {'initial_data': initial_data})

def review_list(request):
    reviews = Review.objects.all().order_by('-id')  # newest first
    return render(request, 'reviews/review_list.html', {'reviews': reviews})