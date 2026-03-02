from django.contrib import admin
from .models import SQLConverterFile


@admin.register(SQLConverterFile)
class SQLConverterFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'uploaded_at', 'conversion_count')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename',)
