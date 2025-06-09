import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from lightgbm import LGBMClassifier
import joblib

# === 1. Veri Yükleme ===
df = pd.read_csv("loan_approval_dataset.csv")
df.columns = df.columns.str.strip()  # Sütun isimlerindeki boşlukları temizle
print("✅ Veri şekli:", df.shape)
print(df.head())

# === 2. Eksik Değer Kontrolü ===
print("\n🔍 Eksik değer kontrolü:")
print(df.isnull().sum())

# === 3. Kategorik Verileri Encode Et ===
categorical_cols = ['education', 'self_employed']
le = LabelEncoder()
for col in categorical_cols:
    df[col] = le.fit_transform(df[col])

# === 4. Hedef Değişkeni Encode Et ===
df['loan_status'] = LabelEncoder().fit_transform(df['loan_status'])  # Approved → 1, Rejected → 0

# === 5. Özellik ve Hedef Ayırma ===
X = df.drop(["loan_id", "loan_status"], axis=1)  # loan_id model için anlamlı değil
y = df["loan_status"]

# === 6. Eğitim-Test Ayırma ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === 7. Ölçekleme ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === 8. Model Eğitimi ===
model = LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train_scaled, y_train)

# === 9. Değerlendirme ===
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"AUC: {roc_auc_score(y_test, y_prob):.4f}")

# === 10. Modeli Kaydet ===
joblib.dump(model, "kredi_modeli.pkl")
joblib.dump(scaler, "kredi_scaler.pkl")
print("✅ Model ve scaler kaydedildi.")
