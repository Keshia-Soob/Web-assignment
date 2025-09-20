from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),   # root page shows KiPouCuit
   
]

