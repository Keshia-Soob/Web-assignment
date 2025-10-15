from django.contrib import admin
from .models import Review
# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'rating', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('rating', 'created_at')