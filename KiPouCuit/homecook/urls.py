from django.urls import path
from . import views

urlpatterns = [
    path('homecook/', views.homecook, name='homecook'),
    path('homecook_log/', views.homecook_log, name='homecook_log'),  # keep existing
    path('homecook/mark-ready/<int:item_id>/', views.mark_order_ready, name='mark_order_ready'),
]