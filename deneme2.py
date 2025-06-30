import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import xgboost as xgb

# 1. Veri Yükle
df = pd.read_csv("loan_approval_dataset.csv")
df.columns = df.columns.str.strip()

# 2. Kategorik Verileri Encode Et
le = LabelEncoder()
df["education"] = le.fit_transform(df["education"])
df["self_employed"] = le.fit_transform(df["self_employed"])
df["loan_status"] = le.fit_transform(df["loan_status"])

# 3. Feature Engineering
df["cibil_group"] = pd.cut(df["cibil_score"], bins=[300, 600, 750, 900], labels=["low", "medium", "high"])
df["cibil_group"] = LabelEncoder().fit_transform(df["cibil_group"].astype(str))

df["total_assets"] = df["residential_assets_value"] + df["commercial_assets_value"] + df["luxury_assets_value"] + df["bank_asset_value"]
df["debt_to_income_ratio"] = df["loan_amount"] / (df["income_annum"] + 1)

# 4. Özellik ve Hedef
drop_cols = ["loan_id", "loan_status", "cibil_score"]  # 'loan_status' hedef, 'cibil_score' çıkarıldı
X = df.drop(columns=drop_cols)
y = df["loan_status"]

# 5. Eğitim-Test Ayrımı
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 6. Ölçekleme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 7. Model
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.1,
    subsample=0.9,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42
)

model.fit(X_train_scaled, y_train)

# 8. Değerlendirme
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"\n🎯 ROC AUC Skoru: {roc_auc_score(y_test, y_prob):.4f}")

# 9. Confusion Matrix (sade)
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix - XGBoost")
plt.xlabel("Tahmin")
plt.ylabel("Gerçek")
plt.tight_layout()
plt.show()

# 10. Doğruluk
print(f"🔍 Eğitim Doğruluğu: {accuracy_score(y_train, model.predict(X_train_scaled)):.4f}")
print(f"🔍 Test Doğruluğu: {accuracy_score(y_test, y_pred):.4f}")

# 11. Kaydetme (Bellek Hatası Olmaması İçin)
joblib.dump(model, "kredi_model_birlesik.pkl")
joblib.dump(scaler, "kredi_scaler_birlesik.pkl")
print("✅ Model ve scaler başarıyla kaydedildi.")
