import streamlit as st
import pandas as pd
import joblib

# === Model ve Scaler ===
model = joblib.load("kredi_modeli_v3.pkl")
scaler = joblib.load("kredi_scaler_v3.pkl")

# === Sayfa Ayarı ===
st.set_page_config(page_title="Kredi Onay Tahmini", layout="centered")
st.title("📊 Kredi Onay Tahmini")
st.markdown("Aşağıdaki bilgileri doldurarak kredi başvurusunun onaylanma olasılığını öğrenin:")

# === Kullanıcı Girdileri ===
no_of_dependents = st.slider("👨‍👩‍👧 Bağımlı Sayısı", 0, 10, 0)
education = st.selectbox("🎓 Eğitim Durumu", ["Lisans Mezunu", "Mezun Değil"])
self_employed = st.selectbox("💼 Serbest Meslek Sahibi mi?", ["Evet", "Hayır"])
income_annum = st.number_input("💰 Yıllık Gelir (₺)", min_value=0)
loan_amount = st.number_input("📄 Talep Edilen Kredi Tutarı (₺)", min_value=0)
loan_term = st.number_input("📆 Kredi Vadesi (Ay)", min_value=1, value=12)
res_assets = st.number_input("🏠 Konut Varlığı (₺)", min_value=0)
comm_assets = st.number_input("🏢 Ticari Varlık (₺)", min_value=0)
lux_assets = st.number_input("💎 Lüks Varlık (₺)", min_value=0)
bank_assets = st.number_input("🏦 Banka Varlığı (₺)", min_value=0)
cibil_score = st.slider("📊 CIBIL Skoru", min_value=300, max_value=900, value=600)

# === Feature Engineering ===
education_encoded = 1 if education == "Lisans Mezunu" else 0
self_employed_encoded = 1 if self_employed == "Evet" else 0
total_assets = res_assets + comm_assets + lux_assets + bank_assets
debt_to_income_ratio = loan_amount / (income_annum + 1)

# === Veri Çerçevesi ===
input_df = pd.DataFrame([[ 
    no_of_dependents,
    education_encoded,
    self_employed_encoded,
    income_annum,
    loan_amount,
    loan_term,
    total_assets,
    debt_to_income_ratio,
    cibil_score
]], columns=[
    'no_of_dependents', 'education', 'self_employed', 'income_annum',
    'loan_amount', 'loan_term', 'total_assets',
    'debt_to_income_ratio', 'cibil_score'
])

# === Sütun sırasını garantiye al ===
input_df = input_df[scaler.feature_names_in_]

# === Ölçekleme ve Tahmin ===
scaled_input = scaler.transform(input_df)

if st.button("🔍 Tahmini Gör"):
    pred = model.predict(scaled_input)[0]
    prob = model.predict_proba(scaled_input)[0][1]

    if pred == 1:
        st.success(f"✅ Kredi ONAYLANABİLİR. Güven düzeyi: %{prob * 100:.2f}")
    else:
        st.error(f"❌ Kredi REDDEDİLEBİLİR. Güven düzeyi: %{prob * 100:.2f}")
