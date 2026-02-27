# 原：只接受 excel
# file = forms.FileField(accept='.xlsx')
import zipfile

# 新：接受 zip + excel
from django.core.exceptions import ValidationError

from django import forms
from .models import ZipFile


def validate_file_type(file):
    """校验文件类型"""
    name = file.name.lower()
    if name.endswith('.zip'):
        # 进一步校验 zip 内容（可选）
        if not zipfile.is_zipfile(file):
            raise ValidationError('无效的 ZIP 文件')
        file.seek(0)  # 重置指针
    elif name.endswith(('.xlsx', '.xls')):
        pass
    else:
        raise ValidationError('仅支持 .zip 或 .xlsx 文件')


class ExcelUploadForm(forms.ModelForm):
    file = forms.FileField(
        validators=[validate_file_type],
        widget=forms.ClearableFileInput(attrs={'accept': '.zip,.xlsx'})
    )

    class Meta:
        model = ZipFile
        fields = ['file']