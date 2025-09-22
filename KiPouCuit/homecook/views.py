from django.shortcuts import render

# Create your views here.
def homecook(request):
    return render(request, 'homecook/homecook.html')