from django.urls import path
from . import views

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('giris/', views.giris_yap, name='giris'),
    path('kayit/', views.kayit_ol, name='kayit'),
    path('cikis/', views.cikis_yap, name='cikis'),
    path('profil/', views.profil, name='profil'),
    path('tahmin/', views.kredi_tahmin, name='kredi_tahmin'),  # ✅ TAHMİN ROTASI
]
