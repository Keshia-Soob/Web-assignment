"""
URL configuration for KiPouCuit project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.urls import include

urlpatterns += [
    path('', include('main_page.urls')),
]

urlpatterns += [
    path('', include('meals.urls')),
]

urlpatterns += [
    path('', include('orders.urls')),
]

urlpatterns += [
    path('', include('reviews.urls')),
]

urlpatterns += [
    path('', include('users.urls')),
]

urlpatterns += [
    path('', include('homecook.urls')),
]

#Serve uploaded media (images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
