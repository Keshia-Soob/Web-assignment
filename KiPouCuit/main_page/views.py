from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'main_page/home.html')  # default title KiPouCuit

def about(request):
    return render(request, 'main_page/about.html')

def contact(request):
    return render(request, 'main_page/contact.html')