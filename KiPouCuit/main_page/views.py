from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
from reviews.models import Review 
from django.contrib.auth.models import User
from meals.models import MenuItem  

# Home Page
def home(request):
    # Get one random meal from each cuisine for best sellers
    best_sellers = []
    cuisines = ['indian', 'mauritian', 'english', 'french', 'asian']
    
    for cuisine in cuisines:
        meal = MenuItem.objects.filter(cuisine=cuisine).order_by('?').first()
        if meal:
            best_sellers.append(meal)
    
    return render(request, 'main_page/home.html', {
        'best_sellers': best_sellers
    })

# About Page with dynamic testimonials
def about(request):
    # Get the 3 latest reviews (newest first)
    raw_reviews = Review.objects.order_by('-created_at')[:3]

    # Attach a profile photo URL when a matching user exists (by email)
    reviews_with_photos = []
    for r in raw_reviews:
        photo_url = None
        try:
            user = User.objects.get(email=r.email)
            # Ensure user has a profile and a photo
            if hasattr(user, 'userprofile') and user.userprofile.photo:
                try:
                    photo_url = user.userprofile.photo.url
                except Exception:
                    photo_url = None
        except User.DoesNotExist:
            photo_url = None

        reviews_with_photos.append({'review': r, 'photo': photo_url})

    return render(request, 'main_page/about.html', {'latest_reviews': reviews_with_photos})

# Contact Page
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message_text
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # prevents resubmission

    return render(request, 'main_page/contact.html')
