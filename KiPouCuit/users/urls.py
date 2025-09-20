from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),  # this is the named URL
    path('homecook/', views.homecook, name='homecook'),
    path('signup/', views.signup, name='signup'),
]