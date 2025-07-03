import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score
from xgboost import XGBClassifier
import joblib
import matplotlib.pyplot as plt

# === 1. Veri Yükleme ===
df = pd.read_csv("loan_approval_dataset_tl.csv")
df.columns = df.columns.str.strip()

# === 2. Kategorik Değerleri Encode Et ===
label_cols = ["education", "self_employed"]
for col in label_cols:
    df[col] = LabelEncoder().fit_transform(df[col])

df['loan_status'] = LabelEncoder().fit_transform(df['loan_status'])

# === 3. CIBIL Skorunu Grupla (FİNDEKS gibi kullanılabilir)
df['cibil_group'] = pd.cut(
    df['cibil_score'],
    bins=[300, 600, 750, 850],
    labels=['low', 'medium', 'high']
)
df['cibil_group'] = LabelEncoder().fit_transform(df['cibil_group'].astype(str))

# === 4. Özellik Mühendisliği ===
df['total_assets'] = df[[
    'residential_assets_value', 'commercial_assets_value',
    'luxury_assets_value', 'bank_asset_value'
]].sum(axis=1)

df['debt_to_income_ratio'] = df['loan_amount'] / (df['income_annum'] + 1)

# === 5. Model Girdileri ===
drop_cols = ["loan_id", "loan_status", "cibil_score"]  # cibil_score çıkarıldı
X = df.drop(columns=drop_cols)
y = df["loan_status"]

# === 6. Eğitim/Test Ayırma ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# === 7. Ölçekleme ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === 8. Model Eğitimi (XGBoost)
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

model.fit(X_train_scaled, y_train)

# === 9. Değerlendirme ===
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"\n🎯 ROC AUC Skoru: {roc_auc_score(y_test, y_prob):.4f}")

cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(confusion_matrix=cm).plot(cmap="viridis")
plt.title("Confusion Matrix - XGBoost (CIBIL Olmadan)")
plt.tight_layout()
plt.show()

# === 10. Kaydet ===
joblib.dump(model, "kredi_model_final.pkl")
joblib.dump(scaler, "kredi_scaler_final.pkl")
print("✅ Model ve scaler başarıyla kaydedildi.")
