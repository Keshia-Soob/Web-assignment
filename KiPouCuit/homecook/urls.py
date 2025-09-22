from django.urls import path
from . import views

urlpatterns = [
    path('homecook/', views.homecook, name='homecook'),  # this is the named URL
]