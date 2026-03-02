from django import forms
from .models import SQLConverterFile


class SQLConverterUploadForm(forms.ModelForm):
    """Excel文件上传表单"""
    class Meta:
        model = SQLConverterFile
        fields = ('file',)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 验证文件扩展名
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("只支持Excel文件 (.xlsx, .xls)")
        return file
