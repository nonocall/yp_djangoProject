from django.urls import path
from . import views



urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('preview/', views.excel_preview, name='excel_preview'),
    path('download/<int:file_id>/', views.download_excel, name='download_excel'),
    # Oracle规则执行
    path('oracle_rule/', views.oracle_rule_upload, name='oracle_rule_upload'),
    path('oracle_rule/preview/', views.get_excel_sheets, name='get_excel_sheets'),
    path('oracle_rule/columns/', views.get_excel_columns, name='get_excel_columns'),
    path('oracle_rule/execute/', views.execute_oracle_rules, name='execute_oracle_rules'),
    path('oracle_rule/progress/<int:execution_id>/', views.get_execution_progress, name='get_execution_progress'),
    path('oracle_rule/download/<int:execution_id>/', views.download_zip, name='oracle_rule_download_zip'),
    path('oracle_rule/history/', views.execution_history, name='oracle_rule_history'),
]