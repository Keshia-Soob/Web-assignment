from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.order, name='order'),
    path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove_from_order/<int:item_id>/', views.remove_from_order, name='remove_from_order'),
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'), 
    path('cart/data/', views.get_cart_data, name='orders_get_cart_data'),
]
