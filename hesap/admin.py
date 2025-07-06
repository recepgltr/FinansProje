from django.contrib import admin
from .models import KullaniciYorumu
admin.site.register(KullaniciYorumu)
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'yayin_tarihi')
    prepopulated_fields = {"slug": ("baslik",)}

# Register your models here.
