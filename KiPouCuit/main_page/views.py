from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
from reviews.models import Review  # import Review model for testimonials

# Home Page
def home(request):
    return render(request, 'main_page/home.html')

# About Page with dynamic testimonials
def about(request):
    # Get the 3 latest reviews (newest first)
    latest_reviews = Review.objects.order_by('-created_at')[:3]
    return render(request, 'main_page/about.html', {'latest_reviews': latest_reviews})

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
