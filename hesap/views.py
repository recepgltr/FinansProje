import os
import joblib
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfilGuncelleForm, KrediTahminForm
from .models import UserProfile

# === MODELİ TEK SEFERDE YÜKLE ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'kredi_modeli_v2.pkl')
kredi_model = joblib.load(MODEL_PATH)

# === Giriş Sayfası ===
def anasayfa(request):
    if request.session.get("giris_basarili"):
        del request.session["giris_basarili"]
    return render(request, 'hesap/anasayfa.html')


def giris_yap(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Tüm alanları doldurunuz.")
            return redirect("anasayfa")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Giriş başarılı ✅")
            request.session["giris_basarili"] = True
            return redirect("anasayfa")
        else:
            messages.error(request, "Kullanıcı adı veya şifre yanlış!")
            return redirect("anasayfa")

    return render(request, "hesap/giris.html")


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


def cikis_yap(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect("anasayfa")


@login_required
def profil(request):
    profil, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfilGuncelleForm(request.POST or None, request.FILES or None, instance=profil)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profil başarıyla güncellendi ✅")
            return redirect("profil")
        else:
            messages.error(request, "Formda hata var. Lütfen tekrar deneyin.")

    return render(request, "hesap/profil.html", {
        "form": form,
        "profil": profil
    })


# === Kredi Tahmin Sayfası ===
from django.contrib.auth.decorators import login_required
import numpy as np

@login_required
def kredi_tahmin(request):
    tahmin = None
    detaylar = {}

    if request.method == "POST":
        form = KrediTahminForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # === education & self_employed (LabelEncoder ile kodlandı)
            education = 1 if data['education'] == "Graduate" else 0
            self_employed = 1 if data['self_employed'] == "Yes" else 0

            # === cibil_group
            score = data['cibil_score']
            if score <= 600:
                cibil_group = 0  # low
                cibil_str = "Düşük"
            elif score <= 750:
                cibil_group = 1  # medium
                cibil_str = "Orta"
            else:
                cibil_group = 2  # high
                cibil_str = "Yüksek"

            # === total_assets & debt_to_income_ratio
            total_assets = (
                data['residential_assets_value'] +
                data['commercial_assets_value'] +
                data['luxury_assets_value'] +
                data['bank_asset_value']
            )
            debt_to_income_ratio = data['loan_amount'] / (data['income_annum'] + 1)

            # === Sıralı giriş verisi (tam 13 özellik)
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

            sonuc = kredi_model.predict(girdi)[0]
            tahmin = "✅ Kredi Onaylandı" if sonuc == 1 else "❌ Kredi Reddedildi"

            detaylar = {
                "toplam_varlik": f"{total_assets:,}".replace(",", "."),
                "cibil": cibil_str,
                "borc_gelir": f"{debt_to_income_ratio:.2f}".replace(".", ",")
            }

    else:
        form = KrediTahminForm()

    return render(request, "hesap/tahmin.html", {
        "form": form,
        "tahmin": tahmin,
        "detaylar": detaylar
    })