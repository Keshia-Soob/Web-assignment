"""
URL configuration for KiPouCuit project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings            # ✅ added
from django.conf.urls.static import static   # ✅ added

urlpatterns = [
    path('admin/', admin.site.urls),

    # your existing app routes
    path('', include('main_page.urls')),
    path('', include('meals.urls')),
    path('', include('orders.urls')),
    path('', include('reviews.urls')),
    path('', include('users.urls')),
    path('', include('homecook.urls')),
]

# ✅ Serve uploaded media (images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

