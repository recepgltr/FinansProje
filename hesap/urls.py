from django.urls import path
from . import views

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('giris/', views.giris_yap, name='giris'),
    path('kayit/', views.kayit_ol, name='kayit'),
    path('cikis/', views.cikis_yap, name='cikis'),
    path('profil/', views.profil, name='profil'),
    path('tahmin/', views.kredi_tahmin, name='kredi_tahmin'),
    path('gecmis/', views.basvuru_gecmisi, name='basvuru_gecmisi'),
    path('basvuru/<int:basvuru_id>/', views.basvuru_detay, name='basvuru_detay'),
    path('basvuru/sil/<int:basvuru_id>/', views.basvuru_sil, name='basvuru_sil'),

]
