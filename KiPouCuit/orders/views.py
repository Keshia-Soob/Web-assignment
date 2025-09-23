from django.shortcuts import render

# Create your views here.
def order(request):
    return render(request, 'orders/order.html')

def order_confirmed(request):
    return render(request, 'orders/order_confirmed.html')

def order_summary(request):
    return render(request, 'orders/order_summary.html')