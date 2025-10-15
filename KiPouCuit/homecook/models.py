from django.db import models

# Create your models here.
class HomeCook(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    cuisine = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='homecook_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} {self.surname} ({self.cuisine})"
