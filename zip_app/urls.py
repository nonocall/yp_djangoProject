from django.urls import path
from . import views



urlpatterns = [
    # path('index/', views.zip_index, name='zip_index'),
    path('upload/', views.upload_zip, name='upload_zip'),
    path('preview/', views.zip_preview, name='zip_preview'),
    path('download/<int:file_id>/', views.download_zip, name='download_zip'),
]