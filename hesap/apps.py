from django.apps import AppConfig

class HesapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hesap'

    def ready(self):
        import hesap.signals  # Kullanıcı oluşturulduğunda UserProfile otomatik oluşsun diye
