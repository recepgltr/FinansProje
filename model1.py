import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
import matplotlib.pyplot as plt
import joblib

# === 1. Veri Yükleme ===
df = pd.read_csv("loan_approval_dataset.csv")
df.columns = df.columns.str.strip()
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
df['loan_status'] = LabelEncoder().fit_transform(df['loan_status'])

# === 5. Feature Engineering ===
df['cibil_group'] = pd.cut(df['cibil_score'], bins=[300, 600, 750, 850],
                           labels=['low', 'medium', 'high'])
df['cibil_group'] = LabelEncoder().fit_transform(df['cibil_group'].astype(str))

df['total_assets'] = df[['residential_assets_value', 'commercial_assets_value',
                         'luxury_assets_value', 'bank_asset_value']].sum(axis=1)

df['debt_to_income_ratio'] = df['loan_amount'] / (df['income_annum'] + 1)

# === 6. Özellik Seçimi ===
drop_cols = ["loan_id", "loan_status", "cibil_score"]  # cibil_score çıkarıldı
X = df.drop(columns=drop_cols)
y = df["loan_status"]

# === 7. Eğitim-Test Ayırma ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === 8. Ölçekleme ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === 9. Model Eğitimi ===
model = LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train_scaled, y_train)

# === 10. Değerlendirme ===
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"AUC: {roc_auc_score(y_test, y_prob):.4f}")

# === 11. Confusion Matrix ===
ConfusionMatrixDisplay.from_estimator(model, X_test_scaled, y_test)
plt.title("Confusion Matrix - LightGBM (engineered features)")
plt.grid()
plt.show()

# === 12. Modeli Kaydet ===
joblib.dump(model, "kredi_modeli_v2.pkl")
joblib.dump(scaler, "kredi_scaler_v2.pkl")
print("✅ Model ve scaler kaydedildi.")

# === 13. Cross-Validation AUC ===
model_cv = LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
cv_auc_scores = cross_val_score(model_cv, X, y, cv=5, scoring='roc_auc')
print("\n📊 Cross-Validation AUC Skorları:", cv_auc_scores)
print("✅ Ortalama AUC:", np.mean(cv_auc_scores))

# === 14. Logistic Regression Benchmark ===
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train_scaled, y_train)
y_prob_lr = lr_model.predict_proba(X_test_scaled)[:, 1]
print("\n📈 Logistic Regression AUC:", roc_auc_score(y_test, y_prob_lr))

# === 15. Korelasyonlar ===
correlations = df.corr(numeric_only=True)
print("\n🔎 loan_status ile korelasyonlar:")
print(correlations["loan_status"].sort_values(ascending=False))

importance = pd.Series(model.feature_importances_, index=X.columns)
importance.nlargest(10).plot(kind='barh')
plt.title("Öznitelik Önem Grafiği")
plt.show()