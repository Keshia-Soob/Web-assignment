from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.order, name='order'),  # this is the named URL
    path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
    path('order_summary/', views.order_summary, name='order_summary'),
]