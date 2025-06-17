import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score
import matplotlib.pyplot as plt

# === 1. Veri Yükleme (daha önce oluşturulmuş veri kullanıldı)
df = pd.read_csv("veri.csv")
  # Eğer yeni başlıyorsan buraya CSV oku: 
# === 2. Label Encoding (kategorik sütunlar)
label_cols = ["meslek", "medeni_durum", "cinsiyet"]
for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

# === 3. Özellikler ve hedef değişken
X = df.drop(columns=["onay"])
y = df["onay"]

# === 4. Eğitim-Test Ayrımı
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === 5. Normalizasyon
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === 6. Random Forest Model Eğitimi
model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X_train_scaled, y_train)

# === 7. Tahminler
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

# === 8. Değerlendirme Metikleri
print("\n📊 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))
print(f"\n🎯 ROC AUC Skoru: {roc_auc_score(y_test, y_prob):.4f}")

# === 9. Confusion Matrix Görselleştirme
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap="Blues")
plt.title("Confusion Matrix - Random Forest")
plt.grid(False)
plt.tight_layout()
plt.show()
