from django.db import models


class ZipFile(models.Model):
    file = models.FileField(upload_to='zip_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.original_filename