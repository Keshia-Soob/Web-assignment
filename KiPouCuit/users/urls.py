from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('user_history/', views.user_history_view, name='user_history'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
]
