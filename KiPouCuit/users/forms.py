from django import forms
from .models import UserProfile

class UserProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']
