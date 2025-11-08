from django.db import models
from django.contrib.auth.models import User


def homecook_profile_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/homecook_profiles/user_<id>/<filename>
    return f'homecook_profiles/user_{instance.user.id}/{filename}'


class HomeCook(models.Model):
    CUISINE_CHOICES = [
        ('indian', 'Indian'),
        ('mauritian', 'Mauritian'),
        ('english', 'English'),
        ('french', 'French'),
        ('asian', 'Asian'),
    ]

    # 🔹 LINK TO DJANGO USER (THIS IS THE IMPORTANT PART)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='homecook'
    )

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    # You can keep this email, but it should match user.email
    email = models.EmailField(unique=True)

    # NOTE: This is NOT used for authentication. Django's User handles real login.
    password = models.CharField(max_length=128)

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    cuisine = models.CharField(max_length=50, choices=CUISINE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=homecook_profile_path,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.get_cuisine_display()})"

