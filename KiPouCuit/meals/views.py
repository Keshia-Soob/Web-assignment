from django.shortcuts import render

# Create your views here.
def menu(request):
    return render(request, 'meals/menu.html')

def addmenu(request):
    return render(request, 'meals/addmenu.html')