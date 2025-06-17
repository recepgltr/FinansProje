# hesap/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dogum_tarihi = models.DateField(null=True, blank=True)
    profil_resmi = models.ImageField(upload_to='profil_resimleri/', null=True, blank=True)
    bio = models.TextField(blank=True)  # ← Bunu da ekledik

    def __str__(self):
        return self.user.username
