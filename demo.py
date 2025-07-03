import pandas as pd

# CSV dosyasını oku
df = pd.read_csv("loan_approval_dataset.csv")

# Sütun isimlerindeki boşlukları temizle
df.columns = df.columns.str.strip()

# Kur oranı (örnek: 0.036 ile TL'den USD'ye çevir)
kur_orani = 0.47

# Dönüştürülecek sütunlar
parasal_sutunlar = [
    "income_annum", "loan_amount", "residential_assets_value",
    "commercial_assets_value", "luxury_assets_value", "bank_asset_value"
]

# Parasal sütunları dönüştür
for sutun in parasal_sutunlar:
    df[sutun] = df[sutun] * kur_orani

# Yeni CSV'yi kaydet
df.to_csv("loan_approval_dataset_tl.csv", index=False)
