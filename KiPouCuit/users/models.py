from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/profile_photos/user_<id>/<filename>
    return f'profile_photos/user_{instance.user.id}/{filename}'


class UserProfile(models.Model):
    STATUS_CHOICES = [
        ("NONE", "None"),
        ("APPROVED", "Approved"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(
        upload_to=user_directory_path,
        default='profile_photos/default.jpg',
        blank=True
    )

    # 🔹 HOMECOOK FIELDS
    is_homecook = models.BooleanField(default=False)
    homecook_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="NONE",
    )
    bio = models.TextField(blank=True)
    specialty = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create/update UserProfile whenever a User is created or saved.
    So you can safely call: request.user.userprofile
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # if somehow no profile exists, create it
        if hasattr(instance, "userprofile"):
            instance.userprofile.save()
        else:
            UserProfile.objects.create(user=instance)
