from django import forms
from .models import UserProfile

# === Profil Güncelleme Formu ===
class ProfilGuncelleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profil_resmi']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Kendiniz hakkında birkaç cümle yazın...',
                'rows': 4
            }),
            'profil_resmi': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

# === Kredi Tahmin Formu ===
class KrediTahminForm(forms.Form):
    no_of_dependents = forms.IntegerField(
        label="Bakmakla Yükümlü Kişi Sayısı", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    education = forms.ChoiceField(
        label="Eğitim Durumu",
        choices=[("Graduate", "Lisans Mezunu"), ("Not Graduate", "Lisans Mezunu Değil")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    self_employed = forms.ChoiceField(
        label="Serbest Meslek",
        choices=[("Yes", "Evet"), ("No", "Hayır")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    income_annum = forms.FloatField(
        label="Yıllık Gelir (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    loan_amount = forms.FloatField(
        label="Kredi Miktarı (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    loan_term = forms.IntegerField(
        label="Kredi Vadesi (Ay)", min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    cibil_score = forms.IntegerField(
        label="CIBIL Skoru (300-900)", min_value=300, max_value=900,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    residential_assets_value = forms.FloatField(
        label="Konut Varlık Değeri (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    commercial_assets_value = forms.FloatField(
        label="Ticari Varlık Değeri (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    luxury_assets_value = forms.FloatField(
        label="Lüks Varlık Değeri (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    bank_asset_value = forms.FloatField(
        label="Banka Varlık Değeri (₺)", min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
