import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import joblib

# === 1. Veri Yükle ===
df = pd.read_csv("loan_approval_dataset.csv")
df.columns = df.columns.str.strip()

# === 2. Encode ===
for col in ['education', 'self_employed']:
    df[col] = LabelEncoder().fit_transform(df[col])
df['loan_status'] = LabelEncoder().fit_transform(df['loan_status'])

# === 3. Özellikler: Total Asset + Debt/Gelir gibi özellikler dahil ===
df['total_assets'] = df[['residential_assets_value', 'commercial_assets_value',
                         'luxury_assets_value', 'bank_asset_value']].sum(axis=1)
df['debt_to_income_ratio'] = df['loan_amount'] / (df['income_annum'] + 1)

# === 4. X ve y Ayır ===
drop_cols = ['loan_id', 'loan_status', 'cibil_score']  # CIBIL çıkarıldı
X = df.drop(columns=drop_cols)
y = df['loan_status']

# === 5. Eğitim/Test Ayrımı ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === 6. Ölçekleme ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === 7. Sınıf Oranına Göre Ağırlık Hesapla ===
neg, pos = np.bincount(y_train)
scale_pos_weight = neg / pos

# === 8. XGBoost Modeli Kur ===
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1.0,
    reg_lambda=1.0,
    scale_pos_weight=scale_pos_weight,
    use_label_encoder=False,
    eval_metric='auc',
    random_state=42
)
model.fit(X_train_scaled, y_train)

# === 9. Tahmin ve Değerlendirme ===
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"\n🎯 ROC AUC Skoru: {roc_auc_score(y_test, y_prob):.4f}")

ConfusionMatrixDisplay.from_estimator(model, X_test_scaled, y_test)
plt.title("Confusion Matrix - XGBoost (CIBIL Olmadan)")
plt.grid(False)
plt.tight_layout()
plt.show()

# === 10. Kaydet ===
joblib.dump(model, "kredi_modeli_xgb.pkl")
joblib.dump(scaler, "kredi_scaler_xgb.pkl")
print("✅ Model ve scaler kaydedildi.")
