from django.urls import path
from . import views

urlpatterns = [
    # Existing pages
    path('order/', views.order, name='order'),
    path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
    path('order_summary/', views.order_summary, name='order_summary'),

    # 🛒 Cart-related routes
    path('add_to_order/<int:item_id>/', views.add_to_order, name='add_to_order'),
    path('remove_from_order/<int:item_id>/', views.remove_from_order, name='remove_from_order'),
    path('clear_order/', views.clear_order, name='clear_order'),
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
]
