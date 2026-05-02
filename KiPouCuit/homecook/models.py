from django.db import models
from django.contrib.auth.models import User


def homecook_profile_path(instance, filename):
    
    return f'homecook_profiles/user_{instance.user.id}/{filename}'


class HomeCook(models.Model):
    CUISINE_CHOICES = [
        ('indian', 'Indian'),
        ('mauritian', 'Mauritian'),
        ('english', 'English'),
        ('french', 'French'),
        ('asian', 'Asian'),
    ]

    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='homecook'
    )

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=128)

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    cuisine = models.CharField(max_length=50, choices=CUISINE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    latitude  = models.FloatField(null=True, blank=True, default=-20.1609)
    longitude = models.FloatField(null=True, blank=True, default=57.4991)
    profile_picture = models.ImageField(
        upload_to=homecook_profile_path,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.get_cuisine_display()})"

