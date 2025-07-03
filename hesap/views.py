import os
import joblib
import numpy as np
import requests
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfilGuncelleForm, KrediTahminForm
from .models import UserProfile, Basvuru
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import KrediTahminSerializer

# === MODELİ VE SCALER'I YÜKLE ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'kredi_model_birlesik.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'kredi_scaler_birlesik.pkl')
kredi_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# === Anasayfa ===
def anasayfa(request):
    if request.session.get("giris_basarili"):
        del request.session["giris_basarili"]

    context = {}

    if request.user.is_authenticated:
        today = timezone.now().date()
        labels, counts = [], []

        for i in range(4, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%d %b"))
            counts.append(Basvuru.objects.filter(tarih__date=day).count())

        toplam = Basvuru.objects.count()
        onay_sayisi = Basvuru.objects.filter(sonuc='Onaylandı').count()
        red_sayisi = toplam - onay_sayisi
        onay_orani = int((onay_sayisi / toplam) * 100) if toplam > 0 else 0
        son_basvuru = Basvuru.objects.filter(user=request.user).order_by('-tarih').first()

        model_basari = 80.5
        model_guncelleme = "Haziran 2025"

        try:
            api_key = "87a957afa3b6b2dbf08ccd85828de8c4"
            url = f"http://data.fixer.io/api/latest?access_key={api_key}&symbols=USD,TRY"
            resp = requests.get(url, timeout=5)
            kur_data = resp.json()

            eur_try = float(kur_data["rates"]["TRY"])
            eur_usd = float(kur_data["rates"]["USD"])
            usd = round(eur_try / eur_usd, 2)
            eur = round(eur_try, 2)
        except Exception as e:
            print("Kur API hatası:", e)
            usd = eur = "-"

        context.update({
            'labels': labels,
            'counts': counts,
            'toplam_basvuru': toplam,
            'onay_sayisi': onay_sayisi,
            'red_sayisi': red_sayisi,
            'onay_orani': onay_orani,
            'son_basvuru': son_basvuru,
            'model_basari': model_basari,
            'model_guncelleme': model_guncelleme,
            'kur_usd': usd,
            'kur_eur': eur,
        })

    return render(request, 'hesap/anasayfa.html', context)

# === Giriş Yap ===
def giris_yap(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Tüm alanları doldurunuz.")
            return redirect("anasayfa")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session["giris_basarili"] = True
            messages.success(request, "Giriş başarılı ✅")
            return redirect("anasayfa")
        else:
            messages.error(request, "Kullanıcı adı veya şifre yanlış!")
            return redirect("anasayfa")

    return render(request, "hesap/giris.html")

# === Kayıt Ol ===
def kayit_ol(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "Tüm alanları doldurmanız gereklidir.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Kullanıcı adı alınmış!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            request.session["giris_basarili"] = True
            messages.success(request, "Kayıt işlemi başarılı ✅")
            return redirect("anasayfa")
    return render(request, "hesap/kayit.html")

# === Çıkış Yap ===
def cikis_yap(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect("anasayfa")

# === Profil ===
@login_required
def profil(request):
    profil, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfilGuncelleForm(request.POST or None, request.FILES or None, instance=profil)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil başarıyla güncellendi ✅")
        return redirect("profil")

    return render(request, "hesap/profil.html", {"form": form, "profil": profil})

# === Kredi Tahmin ===
@login_required
def kredi_tahmin(request):
    tahmin, detaylar, oneriler = None, {}, []

    if request.method == "POST":
        form = KrediTahminForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            education = 1 if data['education'] == "Graduate" else 0
            self_employed = 1 if data['self_employed'] == "Yes" else 0

            score = data['cibil_score']
            if score <= 600:
                cibil_group, cibil_str = 0, "Düşük"
            elif score <= 750:
                cibil_group, cibil_str = 1, "Orta"
            else:
                cibil_group, cibil_str = 2, "Yüksek"

            total_assets = (
                data['residential_assets_value'] +
                data['commercial_assets_value'] +
                data['luxury_assets_value'] +
                data['bank_asset_value']
            )
            debt_to_income_ratio = data['loan_amount'] / (data['income_annum'] + 1)

            girdi = np.array([[
                data['no_of_dependents'],
                education,
                self_employed,
                data['income_annum'],
                data['loan_amount'],
                data['loan_term'],
                data['residential_assets_value'],
                data['commercial_assets_value'],
                data['luxury_assets_value'],
                data['bank_asset_value'],
                cibil_group,
                total_assets,
                debt_to_income_ratio
            ]])

            girdi_scaled = scaler.transform(girdi)
            sonuc = kredi_model.predict(girdi_scaled)[0]
            tahmin = "✅ Kredi Onaylandı" if sonuc == 1 else "❌ Kredi Reddedildi"

            try:
                api_key = "87a957afa3b6b2dbf08ccd85828de8c4"
                url = f"http://data.fixer.io/api/latest?access_key={api_key}&symbols=USD,TRY"
                resp = requests.get(url, timeout=5)
                kur_data = resp.json()

                eur_try = float(kur_data["rates"]["TRY"])
                eur_usd = float(kur_data["rates"]["USD"])
                usd = round(eur_try / eur_usd, 2)
                eur = round(eur_try, 2)
                altin = 2450.00
            except Exception as e:
                print("Kur API hatası:", e)
                usd = eur = altin = None

            Basvuru.objects.create(
                user=request.user,
                sonuc="Onaylandı" if sonuc == 1 else "Reddedildi",
                tarih=timezone.now(),
                no_of_dependents=data['no_of_dependents'],
                education=data['education'],
                self_employed=data['self_employed'],
                income_annum=data['income_annum'],
                loan_amount=data['loan_amount'],
                loan_term=data['loan_term'],
                cibil_score=data['cibil_score'],
                residential_assets_value=data['residential_assets_value'],
                commercial_assets_value=data['commercial_assets_value'],
                luxury_assets_value=data['luxury_assets_value'],
                bank_asset_value=data['bank_asset_value'],
                usd_kuru=usd,
                eur_kuru=eur,
                altin_kuru=altin,
            )

            detaylar = {
                "toplam_varlik": f"{total_assets:,}".replace(",", "."),
                "cibil": cibil_str,
                "borc_gelir": f"{debt_to_income_ratio:.2f}".replace(".", ",")
            }

            if score < 650:
                oneriler.append("CIBIL skorunuz düşük. Ödemelerinizi düzenli yaparak ve borçlarınızı azaltarak skoru artırabilirsiniz.")
            if data['income_annum'] < 120000:
                oneriler.append("Gelir seviyeniz düşük. Kredi alma şansınızı artırmak için gelir kaynaklarınızı artırmanız önerilir.")
            if debt_to_income_ratio > 0.6:
                oneriler.append("Gelir-borç oranınız yüksek. Kredi tutarını azaltmak veya geliri artırmak onay şansını artırabilir.")
    else:
        form = KrediTahminForm()

    return render(request, "hesap/tahmin.html", {
        "form": form,
        "tahmin": tahmin,
        "detaylar": detaylar,
        "oneriler": oneriler
    })

# === Başvuru Geçmişi ===
@login_required
def basvuru_gecmisi(request):
    basvurular = Basvuru.objects.filter(user=request.user).order_by('-tarih')
    return render(request, 'hesap/gecmis.html', {'basvurular': basvurular})

# === Başvuru Detay ===
@login_required
def basvuru_detay(request, basvuru_id):
    basvuru = get_object_or_404(Basvuru, id=basvuru_id, user=request.user)
    return render(request, "hesap/basvuru_detay.html", {"basvuru": basvuru})

# === Başvuru Sil ===
@login_required
def basvuru_sil(request, basvuru_id):
    basvuru = get_object_or_404(Basvuru, id=basvuru_id, user=request.user)
    basvuru.delete()
    messages.success(request, "Başvuru başarıyla silindi.")
    return redirect("basvuru_gecmisi")

@api_view(["POST"])
def kredi_tahmin_api(request):
    serializer = KrediTahminSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        education = 1 if data['education'] == "Graduate" else 0
        self_employed = 1 if data['self_employed'] == "Yes" else 0

        findeks_notu = data['findeks_notu']
        cibil_score = int((findeks_notu / 1900) * 600 + 300)
        if cibil_score <= 600:
            cibil_group = 0
        elif cibil_score <= 750:
            cibil_group = 1
        else:
            cibil_group = 2

        total_assets = (
            data['residential_assets_value'] +
            data['commercial_assets_value'] +
            data['luxury_assets_value'] +
            data['bank_asset_value']
        )
        debt_to_income_ratio = data['loan_amount'] / (data['income_annum'] + 1)

        girdi = np.array([[ 
            data['no_of_dependents'],
            education,
            self_employed,
            data['income_annum'],
            data['loan_amount'],
            data['loan_term'],
            data['residential_assets_value'],
            data['commercial_assets_value'],
            data['luxury_assets_value'],
            data['bank_asset_value'],
            cibil_group,
            total_assets,
            debt_to_income_ratio
        ]])
        girdi_scaled = scaler.transform(girdi)
        sonuc = kredi_model.predict(girdi_scaled)[0]
        tahmin = "Onaylandı" if sonuc == 1 else "Reddedildi"

        return Response({"tahmin": tahmin})
    return Response(serializer.errors, status=400)