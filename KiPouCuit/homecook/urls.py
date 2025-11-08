from django.urls import path
from . import views

urlpatterns = [
    # path('homecook/', views.homecook, name='homecook'),
    path('homecook/become/', views.homecook_onboarding, name='homecook_onboarding'), 
    path('homecook/signup/', views.homecook_signup, name='homecook_signup'),  
    path('homecook_log/', views.homecook_log, name='homecook_log'), 
    path('homecook/mark-ready/<int:item_id>/', views.mark_order_ready, name='mark_order_ready'),
]