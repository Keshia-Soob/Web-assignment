from django.shortcuts import render,redirect
from django.contrib import messages
from .models import ContactMessage

# Create your views here.
def home(request):
    return render(request, 'main_page/home.html')  # default title KiPouCuit

def about(request):
    return render(request, 'main_page/about.html')

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