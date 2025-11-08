from django.urls import path
from . import views
from .views import MenuListView

urlpatterns = [
    path("menu/", MenuListView.as_view(), name="menu"),
    path("menu/add/", views.addmenu, name="addmenu"),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]