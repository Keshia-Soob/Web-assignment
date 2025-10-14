from django.contrib import admin
from .models import Category, MenuItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    ordering = ("sort_order", "name")

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ("name", "category", "cuisine", "price")
    list_filter   = ("category", "cuisine")
    search_fields = ("name", "description")

