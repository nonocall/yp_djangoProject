from django import forms
from .models import ExcelFile


class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ('file',)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 验证文件扩展名
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("只支持Excel文件 (.xlsx, .xls)")
        return file