from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ("name", "cuisine", "price")
    # list_filter   = ("cuisine")
    search_fields = ("name", "description")

