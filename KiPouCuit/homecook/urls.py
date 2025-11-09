from django.urls import path
from . import views

urlpatterns = [
    path('homecook/become/', views.homecook_onboarding, name='homecook_onboarding'),
    path('homecook/signup/', views.homecook_signup, name='homecook_signup'),
    path('homecook/log/', views.homecook_log, name='homecook_log'),

    # State transition endpoints (POST-only)
    path('homecook/accept/<int:item_id>/', views.accept_order, name='accept_order'),
    path('homecook/mark-ready/<int:item_id>/', views.mark_ready, name='mark_ready'),
    path('homecook/mark-delivered/<int:item_id>/', views.mark_delivered, name='mark_delivered'),
]