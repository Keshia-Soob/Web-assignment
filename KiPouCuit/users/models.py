from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/profile_photos/user_<id>/<filename>
    return f'profile_photos/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(
        upload_to=user_directory_path,
        default='profile_photos/default.jpg',
        blank=True
    )

    def __str__(self):
        return self.user.username
