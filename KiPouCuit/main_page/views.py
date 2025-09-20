from django.shortcuts import render

# Create your views here.
def landing(request):
    return render(request, 'main_page/base.html')  # default title KiPouCuit
def index(request):
    return render(request, 'main_page/index.html')

def about(request):
    return render(request, 'main_page/about.html')  # create this template
