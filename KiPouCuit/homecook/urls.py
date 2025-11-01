from django.urls import path
from . import views

urlpatterns = [
    path('homecook/', views.homecook, name='homecook'),
    path('homecook_log/', views.homecook_log, name='homecook_log'),    # this is the named URL
]