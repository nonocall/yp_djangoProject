from django.db import models


class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.original_filename


class OracleRuleExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('error', '错误'),
    ]

    file_name = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=100, blank=True, null=True)
    rule_column = models.CharField(max_length=100)
    sql_column = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    port = models.IntegerField()
    service_name = models.CharField(max_length=100)
    schema = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rules = models.IntegerField(default=0)
    completed_rules = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    zip_file = models.FileField(upload_to='oracle_rule_results/', null=True, blank=True)
    temp_file = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.file_name} - {self.status}"


class OracleRuleResult(models.Model):
    STATUS_CHOICES = [
        ('success', '成功'),
        ('no_result', '无结果'),
        ('error', '错误'),
    ]

    execution = models.ForeignKey(OracleRuleExecution, on_delete=models.CASCADE, related_name='results')
    rule_name = models.CharField(max_length=255)
    sql_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)
    result_file = models.FileField(upload_to='oracle_rule_results/', null=True, blank=True)
    row_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rule_name} - {self.status}"