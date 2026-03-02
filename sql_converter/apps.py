from django.apps import AppConfig


class SqlConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sql_converter'
    verbose_name = 'SQL转换器'
