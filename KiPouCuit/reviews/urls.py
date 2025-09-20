from django.urls import path
from . import views

urlpatterns = [
    path('review/', views.review, name='review'),  # this is the named URL
]