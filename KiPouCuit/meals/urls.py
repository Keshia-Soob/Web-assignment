from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('addmenu/', views.addmenu, name='addmenu'),  # this is the named URL
]