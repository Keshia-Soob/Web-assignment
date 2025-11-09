from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core import signing
from django.conf import settings


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


# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     """
#     Automatically create/update UserProfile whenever a User is created or saved.
#     So you can safely call: request.user.userprofile
#     """
#     if created:
#         UserProfile.objects.create(user=instance)
#     else:
#         # if somehow no profile exists, create it
#         if hasattr(instance, "userprofile"):
#             instance.userprofile.save()
#         else:
#             UserProfile.objects.create(user=instance)

class PaymentMethod(models.Model):
    """
    Fake/stored card for assignment use only.
    We store:
      - masked_card_number (for display)
      - signed_card (signed with Django signing so it's not plain text)
      - expiry_month, expiry_year, card_holder_name
      - is_default
    NOTE: This is NOT production secure. For assignment only.
    """
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="payment_methods")
    card_holder_name = models.CharField(max_length=150)
    masked_card_number = models.CharField(max_length=32)  # e.g. **** **** **** 4242
    signed_card = models.TextField()  # signed/encrypted representation
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.card_holder_name} {self.masked_card_number}"

    @staticmethod
    def sign_card_number(card_number: str) -> str:
        signer = signing.Signer()
        return signer.sign(card_number)

    @staticmethod
    def unsign_card_number(signed: str) -> str:
        signer = signing.Signer()
        return signer.unsign(signed)

    @classmethod
    def create_from_plain(cls, user, card_number, holder_name, expiry_month, expiry_year, is_default=False):
        # mask last 4
        s = "".join(ch for ch in card_number if ch.isdigit())
        last4 = s[-4:] if len(s) >= 4 else s
        masked = f"**** **** **** {last4}"
        signed = cls.sign_card_number(card_number)
        if is_default:
            cls.objects.filter(user=user, is_default=True).update(is_default=False)
        return cls.objects.create(
            user=user,
            card_holder_name=holder_name,
            masked_card_number=masked,
            signed_card=signed,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            is_default=is_default
        )