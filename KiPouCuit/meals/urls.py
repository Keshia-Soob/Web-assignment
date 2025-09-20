from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.menu, name='menu'),  # this is the named URL
]