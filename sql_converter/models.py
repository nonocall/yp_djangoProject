from django.db import models


class SQLConverterFile(models.Model):
    """存储上传的Excel文件"""
    file = models.FileField(upload_to='sql_converter_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)
    converted_filename = models.CharField(max_length=255, blank=True, null=True)
    conversion_count = models.IntegerField(default=0)  # 转换的SQL数量

    def __str__(self):
        return self.original_filename
