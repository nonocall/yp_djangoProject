from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.upload_sql_excel, name='upload_sql_converter'),
    path('preview/', views.sql_converter_preview, name='sql_converter_preview'),
    path('download/converted/<int:file_id>/', views.download_converted_excel, name='download_converted_excel'),
    path('download/original/<int:file_id>/', views.download_original_excel, name='download_original_excel'),
]
