from django.urls import path
from . import views



urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('preview/', views.excel_preview, name='excel_preview'),
    path('download/<int:file_id>/', views.download_excel, name='download_excel'),
]