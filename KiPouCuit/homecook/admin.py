from django.contrib import admin
from .models import HomeCook

# Register your models here.

@admin.register(HomeCook)
class HomeCookAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'cuisine', 'created_at')
    search_fields = ('name', 'surname', 'email', 'cuisine')