from pathlib import Path
from django.contrib.messages import constants as messages  # 💡 Mesaj sistemini dahil ettik

# === Temel Yollar ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Güvenlik Ayarları ===
SECRET_KEY = 'django-insecure-pcd$%le5bcmkm26e@brvxrpz28up!cb1v44yh5%q-3)jp3whl3'
DEBUG = True
ALLOWED_HOSTS = []

# === Uygulamalar ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hesap',  # ← kendi app'in
    'rest_framework',
]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === URL ve WSGI ===
ROOT_URLCONF = 'kredi_site.urls'
WSGI_APPLICATION = 'kredi_site.wsgi.application'

# === Şablonlar ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === Veritabanı ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === Şifre Doğrulama ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Uluslararasılaştırma ===
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# === Statik Dosyalar ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# === Medya Dosyaları ===
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === Varsayılan Otomatik Alan Tipi ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === Mesaj Sistemi Ayarları ===
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
# settings.py
LOGIN_URL = '/giris/'
