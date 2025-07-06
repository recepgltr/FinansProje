# hesap/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dogum_tarihi = models.DateField(null=True, blank=True)
    profil_resmi = models.ImageField(upload_to='profil_resimleri/', null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Basvuru(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tarih = models.DateTimeField(auto_now_add=True)
    sonuc = models.CharField(max_length=20)

    # Form verileri
    no_of_dependents = models.IntegerField(null=True, blank=True)
    education = models.CharField(max_length=20, null=True, blank=True)
    self_employed = models.CharField(max_length=10, null=True, blank=True)
    income_annum = models.IntegerField(null=True, blank=True)
    loan_amount = models.IntegerField(null=True, blank=True)
    loan_term = models.IntegerField(null=True, blank=True)
    cibil_score = models.IntegerField(null=True, blank=True)
    residential_assets_value = models.IntegerField(null=True, blank=True)
    commercial_assets_value = models.IntegerField(null=True, blank=True)
    luxury_assets_value = models.IntegerField(null=True, blank=True)
    bank_asset_value = models.IntegerField(null=True, blank=True)

    # 🔄 Yeni Eklenen Döviz ve Altın Kurları
    usd_kuru = models.FloatField(null=True, blank=True)
    eur_kuru = models.FloatField(null=True, blank=True)
    altin_kuru = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sonuc} ({self.tarih.strftime('%d.%m.%Y')})"

class KullaniciYorumu(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    yorum = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kullanici.username} - {self.tarih.strftime('%Y-%m-%d')}"
    

class BlogPost(models.Model):
    baslik = models.CharField(max_length=200)
    icerik = models.TextField()
    yazar = models.ForeignKey(User, on_delete=models.CASCADE)
    yayin_tarihi = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=200)

    class Meta:
        ordering = ['-yayin_tarihi']

    def __str__(self):
        return self.baslik